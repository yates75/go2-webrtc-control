import pickle

with open("lidar_recording/frame_0000.pkl", "rb") as f:
    frame = pickle.load(f)

print(type(frame))
if isinstance(frame, dict):
    print(frame.keys())
    for key, value in frame.items():
        print(f"  {key}: {type(value).__name__}", end="")
        if hasattr(value, "__len__"):
            print(f" (len={len(value)})")
        else:
            print(f" = {value!r}")

    # positions/uvs/indices are flat mesh vertex-buffer arrays (see
    # STUDENT_TUTORIAL.md Part 3) -- reshape positions into (x, y, z) points.
    positions = frame["positions"].reshape(-1, 3)
    print(f"\n{positions.shape[0]} points, first 5:")
    print(positions[:5])