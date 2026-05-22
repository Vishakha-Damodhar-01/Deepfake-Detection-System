from tensorflow.keras.models import load_model

print("Loading old .h5 model...")
# Load the model without compiling it to avoid optimizer errors
model = load_model("deepfake_model_v2.h5", compile=False)

print("Saving as new .keras model...")
# Save it in the new, modern format
model.save("deepfake_model_v2.keras")

print("Done! You can now upload deepfake_model_v2.keras to GitHub.")