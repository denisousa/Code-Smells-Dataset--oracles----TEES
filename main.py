import pandas as pd
import re

dataset_context = [
    {
        "file-path": "long-method-2020+2019+2018.csv",
        "new-file-path": "long-method-2020+2019+2018-no-duplication.csv",
        "oracle_result": "is_long_method"
    },
    # {
    #     "file-path": "god-class-2020+2019+2018.csv",
    #     "new-file-path": "god-class-2020+2019+2018-no-duplication.csv",
    #     "oracle_result": "is_god_class"
    # },
    # {
    #     "file-path": "feature-envy-2020+2019+2018.csv",
    #     "new-file-path": "feature-envy-2020+2019+2018-no-duplication.csv",
    #     "oracle_result": "is_feature_envy"
    # },
]


def concatenate_columns(df):
    try:
        return (
            df["project"].astype(str) + " " + df["package"].astype(str) + " " + df["complextype"].astype(str) + " " + df["method"].astype(str)
        )
    except:
        return (
            df["project"].astype(str) + " " + df["package"].astype(str) + " " + df["complextype"].astype(str) + " "
        )
    
def find_method_signature(java_code, method_signature):
    escaped_signature = re.escape(method_signature)
    method_pattern = rf'{escaped_signature}\s*\(*'
    
    match = re.search(method_pattern, java_code)

    if not match:
        return "Method not found."

    start_pos = match.start()

    open_braces = 0
    find = False
    end_pos = start_pos
    java_code_split = java_code.split("\n")
    start_pos = 0

    for i, line in enumerate(java_code_split):
        if method_signature in line:
            start_pos = i
            find = True
            continue

        elif line in '}' and find:
            end_pos =  i + start_pos
            break

    return java_code[start_pos+1:end_pos]

def get_code(df):
    open('erros.txt', 'a').write("")

    code_snippets = []
    for index, row in df.iterrows():
        method_signature = row["method"].split("(")[0]
        row["complextype"] = row["complextype"].replace(".", "/")
        code_path = row["project"] + "/src/" + row["complextype"] + ".java"

        print(code_path)
        try:
            complete_code_str = open(code_path, 'r').read()
            code_str = find_method_signature(complete_code_str, method_signature)
        except:
            code_str = "Code not found"
            open('erros.txt', 'w').write(f"{index} - {code_path}")

        code_snippets.append(code_str)
    
    df["code"] = code_snippets

    return df

def update_oracle_result(df, unique_values_concatenated):
    for value in unique_values_concatenated:
        grouped_data[value] = df[df['concatenated'] == value]

        qtd_true = list(df[df['concatenated'] == value][code_smell_context["oracle_result"]]).count(True)
        qtd_false = list(df[df['concatenated'] == value][code_smell_context["oracle_result"]]).count(False)

        if qtd_true > qtd_false:
            df.loc[df['concatenated'] == value, code_smell_context["oracle_result"]] = True
        else:
            df.loc[df['concatenated'] == value, code_smell_context["oracle_result"]] = False

    return df



total_rows = 0
for code_smell_context in dataset_context:
    df = pd.read_csv(code_smell_context["file-path"])

    df["concatenated"] = concatenate_columns(df)

    unique_values_concatenated = df['concatenated'].unique()
    grouped_data = {}
    
    df = update_oracle_result(df, unique_values_concatenated)
    df = get_code(df)
    df = df.drop(columns=["username"])
    df = df.drop_duplicates(subset=["concatenated"])
    df.to_csv(code_smell_context["new-file-path"], index=False)

    print(df.head())
    print(df.shape)
    total_rows += df.shape[0]
    
print(total_rows)
