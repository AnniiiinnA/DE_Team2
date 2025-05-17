import pandas as pd

def get_demographics(file):
    '''
    Takes file name of wide formatted questionnaire data and returns DataFrame
    of demographic responses indexed by participant ID
    '''

    raw_df = pd.read_csv(file)
    df = pd.DataFrame()
    df["Participant ID"] = raw_df["Participant Private ID"].dropna().astype(int)

    # Get all single-option responses
    cols = ["Multiple Choice object-2 Response",
            "Multiple Choice object-3 Response",
            "Multiple Choice object-4 Response",
            "Multiple Choice object-6 Response",
            "Multiple Choice object-7 Response",
            "Multiple Choice object-8 Response",
            "Multiple Choice object-9 Response"]
    for col in cols:
        df[raw_df[col][0]] = raw_df[col].iloc[1:]

    # Get multi-choice responses one-hot encoded
    race_cols = ["Multiple Choice object-5 American Indian or Alaskan Native",
                 "Multiple Choice object-5 Asian",
                 "Multiple Choice object-5 Black or African American",
                 "Multiple Choice object-5 Native Hawaiian and Other Pacific Islander",
                 "Multiple Choice object-5 White",
                 "Multiple Choice object-5 __other",
                 "Multiple Choice object-5 Other"]
    for col in race_cols:
        df[col[25:]] = raw_df[col].iloc[1:]
    df.set_index("Participant ID", inplace=True)

    return df


def get_fatigue_task(file):
    '''
    Takes file name of task data and returns DataFrame of response, position,
    and reaction time for each fatigue trial.
    '''

    raw_df = pd.read_csv(file)
    df = pd.DataFrame()
    # Only get response rows
    mask = raw_df["Response Type"] == "response"

    # Extract relevant columns
    df["Participant ID"] = raw_df[mask]["Participant Private ID"].astype(int)
    cols = ["Display",
            "Response",
            "Reaction Time",
            "Spreadsheet: Product"]
    for col in cols:
        df[col] = raw_df[mask][col]

    # Filter for rows where 'Display' contains 'Fatigue'
    df = df[df["Display"].str.contains("Discounts Fatigue", case=False, na=False)]

    # Merge position and response rows
    df = df.reset_index(drop=True)
    merged_rows = []

    for i in range(0, len(df)-1, 2):
        row1 = df.iloc[i]
        row2 = df.iloc[i + 1]

        merged_row = {
            "Participant ID": row1["Participant ID"],
            "Display": row1["Display"],
            "Spreadsheet: Product": row1["Spreadsheet: Product"],
            "Response": row1["Response"],        # The actual choice
            "Position": row2["Response"],        # The position
            "Reaction Time": row1["Reaction Time"]
        }

        merged_rows.append(merged_row)
    merged_df = pd.DataFrame(merged_rows)

    
    return merged_df


def get_main_task(file):
    '''
    Takes file name of task data and returns DataFrame of response, position,
    reaction time, and followup questions for each main trial.
    '''

    raw_df = pd.read_csv(file)
    df = pd.DataFrame()
    # Only get response rows
    mask = raw_df["Response Type"] == "response"

    # Extract relevant columns
    df["Participant ID"] = raw_df[mask]["Participant Private ID"].astype(int)
    cols = ["Display",
            "Response",
            "Reaction Time",
            "Spreadsheet: Product",
            "Object Name"]
    for col in cols:
        df[col] = raw_df[mask][col]

    # Filter for rows where 'Display' contains 'Fatigue'
    df = df[df["Display"].str.contains("Discounts Main", case=False, na=False)]

    # Merge position and response rows
    df = df.reset_index(drop=True)
    merged_rows = []

    for i in range(0, len(df)-1, 7):
        row1 = df.iloc[i]
        row2 = df.iloc[i + 1]
        followup = []

        merged_row = {
            "Participant ID": row1["Participant ID"],
            "Display": row1["Display"],
            "Spreadsheet: Product": row1["Spreadsheet: Product"],
            "Response": row1["Response"],        # The actual choice
            "Position": row2["Response"],        # The position
            "Reaction Time": row1["Reaction Time"]
        }

        if "now" in merged_row["Response"]:
            merged_row["Deal Type"] = "Now price"
        elif "get" in merged_row["Response"]:
            merged_row["Deal Type"] = "BOGO"
        elif r"% off" in merged_row["Response"]:
            merged_row["Deal Type"] = "Percentage off"
        else:
            merged_row["Deal Type"] = "Dollar off"

        for k in range(2,7):
            followup = df.iloc[i + k]
            merged_row[followup["Object Name"]] = followup["Response"]

        merged_rows.append(merged_row)
    merged_df = pd.DataFrame(merged_rows)

    
    return merged_df

if __name__ == "__main__":

    outfolder = "processed_pilot_data/"
    questfile = "full_pilot_data/data_exp_226813-vall_questionnaires.csv"
    taskfile = "full_pilot_data/data_exp_226813-vall_tasks.csv"
    demographics = get_demographics(questfile)
    fatigue = get_fatigue_task(taskfile)
    main = get_main_task(taskfile)
    demographics.to_csv(f'{outfolder}demographics.csv', index=True)
    fatigue.to_csv(f"{outfolder}fatigue_trials.csv", index=False)
    main.to_csv(f"{outfolder}main_trials.csv", index=False)

