import csv
# import keyboard

def interactive_labeling(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        writer.writerow(["ingredient_1", "ingredient_2", "label"])  # Header

        next(reader)  # Skip header

        for i, row in enumerate(reader, 1):
            ing1, ing2 = row
            print(f"\nPair {i}: {ing1}, {ing2}")
            print("Enter similarity label (1=least similar, 5=most similar, 0=skip). Press 'q' to exit.")

            while True:
                try:
                    inp = input("Your label: ")
                    if inp == "q":
                        print("\nExiting...")
                        return
                    elif int(inp) in {0, 1, 2, 3, 4, 5}:
                        break
                    else:
                        print("Please enter 0, 1, 2, 3, 4, or 5.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
                except KeyboardInterrupt:
                    print("\nInterrupted. Saving and exiting...")
                    return

            if int(inp) != 0:
                writer.writerow([ing1, ing2, inp])
                print(f"Saved: {ing1}, {ing2}, {inp}")
            else:
                print(f"Skipped: {ing1}, {ing2}")

            # Flush to ensure data is written to disk
            outfile.flush()

    print(f"\nLabeling complete! Labeled pairs saved to {output_file}")

if __name__ == "__main__":
    interactive_labeling("danish_ingredient_pairs.csv", "labeled_danish_ingredient_pairs.csv")