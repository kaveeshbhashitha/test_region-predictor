from db import get_all_user_predictions, get_all_batch_predictions

print("=== User Predictions ===")
for row in get_all_user_predictions():
    print(row)

print("\n=== Batch Predictions ===")
for row in get_all_batch_predictions():
    print(row)
