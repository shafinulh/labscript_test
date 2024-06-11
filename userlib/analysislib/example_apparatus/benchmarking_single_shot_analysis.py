import lyse
import matplotlib.pyplot as plt

# Is this script being run from within an interactive lyse session?
if lyse.spinning_top:
    # If so, use the filepath of the current shot
    h5_path = lyse.path
else:
    # If not, get the filepath of the last shot of the lyse DataFrame
    df = lyse.data()
    h5_path = df.filepath.iloc[-1]

run = lyse.Run(h5_path)

# Get a dictionary of the global variables used in this shot
run_globals = run.get_globals()
run_globals = run 

# extract the traces
trace_names = [
    "AO_ramp",
    # "dummy_measurement_AO_0_fast",
    "AI_signal",
    # "dummy_measurement_slow",
    # "dummy_measurement_med"
]
trace_data = {}

for trace_name in trace_names:
    trace_data[trace_name] = run.get_trace(trace_name)

plt.figure(figsize=(10, 6))

for trace_name, (time, values) in trace_data.items():
    plt.plot(time, values, label=trace_name)


plt.ylim(0, 3.1)

plt.xlabel('Time')
plt.ylabel('Values')
plt.title('Trace Plots')
plt.legend()
plt.grid(True)

plt.show()

# Compute a result based on the data processing and save it to the 'results' group of
# the shot file
ai1_int = trace_data["AO_ramp"][1].sum()
run.save_result('ai1 integrated', ai1_int)
