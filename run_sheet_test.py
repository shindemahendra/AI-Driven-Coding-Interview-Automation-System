from src.utils.sheet_reader_oauth import read_latest_score

if __name__ == "__main__":
    sheet_id = input("Enter Google Sheet ID: ").strip()

    email, score = read_latest_score(sheet_id)

    print("\n=== Latest Response ===")
    print("Email:", email)
    print("Score:", score)
