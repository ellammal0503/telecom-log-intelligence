from src.ingestion.generate_logs import generate_all
from src.features.build_features import build_features
from src.models.train_model import train_model

def run_pipeline():
    print("Step 1: Generating logs...")
    generate_all()

    print("Step 2: Building features...")
    build_features()

    print("Step 3: Training model...")
    train_model()

    print("🚀 Pipeline completed successfully!")

if __name__ == "__main__":
    run_pipeline()