def display_candidates():
    candidates = ["Candidate A", "Candidate B", "Candidate C"]

    print("\n=== AlgoVote ===")
    print("Candidates:")

    for i, candidate in enumerate(candidates, start=1):
        print(f"{i}. {candidate}")

    return candidates


def vote(candidates):
    try:
        choice = int(input("\nEnter your vote (1-3): "))

        if 1 <= choice <= len(candidates):
            print(f"\nYou voted for {candidates[choice - 1]}")
            print("Vote recorded successfully!")
        else:
            print("Invalid choice.")

    except ValueError:
        print("Please enter a valid number.")


if __name__ == "__main__":
    candidates = display_candidates()
    vote(candidates)
