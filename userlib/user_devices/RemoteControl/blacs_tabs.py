"""
Defining the GUI:

To start it will only contain:
    - An AO to which we can write values
    - a Read only cell where we recieve the remote values 
"""
import labscript_utils.h5_lock
import h5py
from labscript_utils import dedent
from qtutils.qt import QtWidgets, QtGui, QtCore
from qtutils import qtlock

from blacs.device_base_class import (
    DeviceTab,
    define_state,
    MODE_BUFFERED,
    MODE_MANUAL,
    MODE_TRANSITION_TO_BUFFERED,
    MODE_TRANSITION_TO_MANUAL,
)
import threading
import zmq

from qtutils import qtlock

import warnings

"""
TODO:
- need to handle widgets for boolean values along with the Analog monitors
    - retrieve boolean value and then update the boolean indicator as necessary

- make the overall COMMS_ENABLE a nicer interface 
"""

class RemoteControlTab(DeviceTab):
    def initialise_GUI(self):
        connection_table = self.settings['connection_table']
        # Retrieve the device connection object that contains information about all the 
        # experimental setup.
        device = connection_table.find_by_name(self.device_name)
        self.properties = device.properties

        self.child_output_connections = []
        self.child_output_devices = []
        self.child_monitor_connections = []
        self.child_monitor_devices = []

        for device in device.child_list.values():
            if device.device_class == "RemoteAnalogOut":
                self.child_output_devices.append(device)
                self.child_output_connections.append(device.parent_port)
            elif device.device_class == "RemoteAnalogMonitor":
                self.child_monitor_devices.append(device)
                self.child_monitor_connections.append(device.parent_port)
            else:
                # throw an error
                pass

        AO_base_step = 0.01
        
        # Remote Output Value Widgets
        AO_prop = {}
        for analog_out_device in self.child_output_devices:
            child_properties = analog_out_device._properties
            AO_prop[analog_out_device.parent_port] = {
                'base_unit': child_properties["units"],
                'min': 0,
                'max': 1000,
                'step': AO_base_step,
                'decimals': child_properties["decimals"],
            }
        self.create_analog_outputs(AO_prop)
        _, self.AO_widgets, _ = self.auto_create_widgets()
        self.auto_place_widgets(("Analog Outputs", self.AO_widgets))

        # Remote Monitor Value Widgets
        AM_prop = {}
        for analog_monitor_device in self.child_monitor_devices:
            child_properties = analog_monitor_device._properties
            AM_prop[analog_monitor_device.parent_port] = {
                'base_unit': child_properties["units"],
                'min': 0,
                'max': 1000,
                'step': AO_base_step,
                'decimals': child_properties["decimals"],
            }
        self.create_analog_outputs(AM_prop)
        _, self.AM_widgets, _ = self.create_subset_widgets(AM_prop)
        self.auto_place_widgets(("Analog Monitors", self.AM_widgets))
        
        for _, widget in self.AM_widgets.items():
            widget.setEnabled(False)

        self.main_gui_layout = self.get_tab_layout()
        # Enable Comms Checkbox
        self.comms_check_box = QtWidgets.QCheckBox("Disable Input")
        self.main_gui_layout.addWidget(self.comms_check_box)
        self.comms_check_box.toggled.connect(self.on_checkbox_toggled)

        # Store references to all widgets in the main gui layout
        self.main_gui_widgets = []
        for i in range(self.main_gui_layout.count()):
            widget = self.main_gui_layout.itemAt(i).widget()
            if widget:
                self.main_gui_widgets.append(widget)
        
        # Connection Failed Button
        # TODO: define the failed button layout in the QT designer application and store in .ui file
        self.center_layout = QtWidgets.QVBoxLayout()
        self.center_layout.setAlignment(QtCore.Qt.AlignCenter)

        self.failed_button = QtWidgets.QPushButton("CONNECTION FAILED, CLICK TO RECONNECT")
        self.failed_button.clicked.connect(lambda _:self.connect_to_remote())

        self.failed_button.setStyleSheet("""
            QPushButton {
                color: white;
                font-weight: bold;
                background-color: #ff6666;
                border: 2px solid #ff4d4d;
                border-radius: 10px;
                padding: 20px 40px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #ff4d4d;
            }
            QPushButton:pressed {
                background-color: #ff3333;
            }
        """)

        self.center_layout.addStretch(1)
        self.center_layout.addWidget(self.failed_button, alignment=QtCore.Qt.AlignCenter)
        self.center_layout.addStretch(1)

        self.main_gui_layout.addLayout(self.center_layout)

        self.failed_button.hide()

        # Manage connection to the remote server
        self.polling = False
        self.connected = False
        self.condition = threading.Condition()

        # self.remote_subscriptions = threading.Thread(target = self.remote_subscriber)
        # self.remote_subscriptions.daemon=True
        # self.remote_subscriptions.start()

    def initialise_workers(self):
        # Create the worker
        self.create_worker(
            "main_worker",
            "user_devices.RemoteControl.blacs_workers.RemoteControlWorker",
            {
                "mock": self.properties['mock'],
                "ip_address": self.properties['ip_address'],
                "port": self.properties['port'],
                "child_output_connections": self.child_output_connections,
                "child_monitor_connections": self.child_monitor_connections,
            }
        )
        self.primary_worker = "main_worker"

        if self.properties['mock']:
            self.connected = True
            self.manual_remote_polling()
        else:
            self.connect_to_remote()
            
        self._can_check_remote_values = True

    def manual_remote_polling(self, enable_comms_state=False):    
        # Start up the remote value polling
        if not self.polling:
            self.statemachine_timeout_add(500, self.status_monitor)
            self.statemachine_timeout_add(5000, self.check_remote_values) 
            self.polling = True
        else: 
            if enable_comms_state:
                self.statemachine_timeout_remove(self.check_remote_values_allowed)  
                self.statemachine_timeout_add(5000, self.check_remote_values)  
            else:
                self.statemachine_timeout_remove(self.check_remote_values) 
                # start up the remote value check which gracefully updates the FPV 
                self.statemachine_timeout_add(500, self.check_remote_values_allowed)  

    @define_state(MODE_MANUAL, True)
    def connect_to_remote(self):
        self.connected = yield(self.queue_work(self.primary_worker, 'connect_to_remote'))
        with self.condition:
            if self.connected:
                self.condition.notify_all()
                self.show_main_gui()    
                self.manual_remote_polling()
            else:
                self.show_failed_connection()

    def show_failed_connection(self):
        with qtlock:
            for widget in self.main_gui_widgets:
                widget.hide()
            self.failed_button.show()

    def show_main_gui(self):
        with qtlock:
            self.failed_button.hide()
            for widget in self.main_gui_widgets:
                widget.show()

    @define_state(MODE_MANUAL, True)
    def on_checkbox_toggled(self, state):
        with qtlock:
            for _, widget in self.AO_widgets.items():
                widget.setEnabled(not state)
        
        self.manual_remote_polling(state)

        kwargs = {'enable_comms': not state}
        yield(self.queue_work(self.primary_worker, 'update_settings', **kwargs))

    # Function to update the GUI with the most recent value of the actual 
    # value of the remote Device
    @define_state(
        MODE_MANUAL|MODE_BUFFERED|MODE_TRANSITION_TO_BUFFERED|MODE_TRANSITION_TO_MANUAL,True,
    )
    def status_monitor(self):
        response = yield (
            self.queue_work(self.primary_worker, "check_status")
        )
        for connection, value in response.items():
            # with qtlock:
            self._AO[connection].set_value(float(value), program=False, update_gui=True)
        return response

    # def remote_subscriber(self):
    #     self.established = False
    #     self.logger.debug("want to connect to remote publisher")
    #     while True:
    #         with self.condition:
    #             while not self.connected:
    #                 self.condition.wait()
    #             self.established = False
    #             self.logger.debug("Processing started")

    #         while self.connected:
    #             if not self.established:
    #                 table = self.settings['connection_table']
    #                 properties = table.find_by_name(self.device_name).properties
    #                 host = properties["ip_address"]
    #                 port = properties["port"]

    #                 # connect to server
    #                 context = zmq.Context()
    #                 x_subscriber = context.socket(zmq.SUB)
    #                 x_subscriber.connect(f"tcp://{host}:{55536}")
    #                 x_subscriber.setsockopt_string(zmq.SUBSCRIBE, "laser_x")

    #                 y_subscriber = context.socket(zmq.SUB)
    #                 y_subscriber.connect(f"tcp://{host}:{55536}")
    #                 y_subscriber.setsockopt_string(zmq.SUBSCRIBE, "laser_y")

    #                 poller = zmq.Poller()
    #                 poller.register(x_subscriber, zmq.POLLIN)
    #                 poller.register(y_subscriber, zmq.POLLIN)

    #                 self.established = True
                
    #             ## NON BLOCKING THREAD
    #             try:
    #                 socks = dict(poller.poll())
    #                 if x_subscriber in socks:
    #                     message = x_subscriber.recv_string()
    #                     self.logger.debug(f"Received on socket1: {message}")
    #                     # Process message for topic1
                    
    #                 if y_subscriber in socks:
    #                     message = y_subscriber.recv_string()
    #                     self.logger.debug(f"Received on socket2: {message}")
    #                     # Process message for topic2
                    
    #             except KeyboardInterrupt:
    #                 break
                                
    #         self.logger.debug("Connection suspended")
