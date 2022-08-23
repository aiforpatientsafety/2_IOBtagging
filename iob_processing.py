# import libraries
from pathlib import Path
import pandas as pd
import datetime as dt
import os
# import glob

from tqdm import tqdm
import sentencepiece as spm


#---------------------- FUNCTIONS --------------------------------
def intersection(lst1, lst2):
    """Find common elements from two lists"""
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def diff_tokens(tokens, tokens_sp):
    """ Find unknown tokens from actual token list 
    Parameters
    ----------
    tokens : list
        unknown token included tokenized list
    tokens_sp : list
        actual tokenized list 
    
    Returns
    -------
    arr: list 
        Filtering all unknown tokens from actual tokenized list
    """
    arr = []
    for idx, tok in enumerate(tokens):
        if tok != tokens_sp[idx]:

            d = {}
            d[tokens_sp[idx]] = tok
            arr.append(d)
    return arr


def tokenize_reports(text):
    """ Sentence piece tokenizing 
    Parameters
    ----------
    text : str
        A raw report (not tokenized)
    
    Returns
    -------
    tokenized_text: list
        Tokenized reports 
    diff_unk: list 
        Containing all unknown tokens for later use
    """
    tokenized_text_ids = tokenizer.encode(text)
    tokenized_text = [tokenizer.IdToPiece(i) for i in tokenized_text_ids]
    tokenized_text_raw = tokenizer.encode(text, out_type=str)
    diff_unk = diff_tokens(tokenized_text_raw, tokenized_text)
    return tokenized_text, diff_unk


def unite_iob(arr1, arr2):
    """ Uniting all single entity IOB token arrays as one token list
    Parameters
    ----------
    arr1 : list
        Enumerating all elements then add it arr2 if not in arr2
    arr2 : list
        Add arr1 elements on it if element is not equal "O"

    Returns
    -------
    str_ : list
        Concatenated list from arr1 and arr2
    """
    str_ = []
    for idx, ele in enumerate(arr1):
        if ele != 'O':
            str_.append(ele)
        elif arr2[idx] != 'O':
            str_.append(arr2[idx])
        else:
            str_.append(ele)
    return str_


def tag_iob(start, end, ts, tp, unk_token):
    """ Uniting all single entity IOB token arrays as one token list
    Parameters
    ----------
    start : int
        entity start position index
    end : int
        entity end position index 
    ts : list
        tokenized reports
    tp: str
        one of entity extraction, intention factuality, relation annotation labels
    unk_token: list
        unknown tokens for calculating entity position index

    Returns
    -------
    res : list
        IOB tagged result from tokenized reports
    """

    # find token position indexes then insert it in one array
    char_number = []
    c = 0
    dif = 0
    for t in ts:
        if t == "▁":
            char_number.append(-1)
        elif t == "<unk>":
            c = c + len(unk_token[dif]["<unk>"])
            char_number.append(c)
            dif += 1
        else:
            t = t.replace("▁", "")
            c = c + len(t)
            char_number.append(c)

    # from token position indexes find entity position then tag it as IOB
    res = ""
    for idx, n in enumerate(char_number):
        if n == -1:
            res = res + "O"
        else:
            if idx == 0:
                if len(intersection(list(range(start, end)), list(range(0,
                                                                        n)))):
                    res = res + "I"
                else:
                    res = res + "O"
            else:
                if len(
                        intersection(list(range(start, end)),
                                     list(range(char_number[idx - 1], n)))):
                    res = res + "I"
                else:
                    res = res + "O"

    # Add "B" tag if token is the beginning of "I" tags
    res = list(res)
    for c in range(len(res) - 1):
        if (res[c] == "O") and (res[c + 1] == "I"):
            res[c + 1] = "B"
        if res[0] == "I":
            res[0] = "B"
    for idx, ele in enumerate(res):
        if ele in ["B", "I"]:
            res[idx] = ele + f"-{tp}"

    return res


#------------------ READING FILES --------------------------------

# Inputing corpus 517 data
path_in = Path.cwd() / "/Users/od/Desktop/past_projects/incident_report/deliverables/AI_phase/iob/data/in/test.xlsx"
df = pd.read_excel(path_in, index_col=0).reset_index(drop=True)

tokenizer = spm.SentencePieceProcessor("./wiki-ja.model")

#------------------ PREPROCESSING DATA ---------------------------
df.label = df.label.fillna(
    "NA")  # prevent "NA" label inserted as nan value in dataframe
# df["index"] = df["index"].astype(str)  # change column type as string

# SentencePiece tokenizing all reports also find all unknown tokens
for idx, row in tqdm(df.loc[0:].iterrows()):
    rep_tokenized, diff_unk = tokenize_reports(row.reports.lower())
    df.loc[idx, "report_tokenized"] = str(rep_tokenized)
    df.loc[idx, "unk_tokens"] = str(diff_unk)

# Convert list inserted as string to actual list
df.report_tokenized = df.report_tokenized.apply(eval)
df.unk_tokens = df.unk_tokens.apply(eval)

# IOB tagging on tokenized reports
for idx, row in tqdm(df.loc[0:].iterrows()):
    rep_tok = row.report_tokenized
    start = row.start_idx
    end = row.end_idx
    ent = row.entity_name
    ### Choosing one of entity, label, relation_index column for IOB tagging (change below to produce IOB for other column)
    ent_type = row.relation_index
    unk_tokens = row.unk_tokens
    df.loc[idx, "tagged_iob"] = str(
        tag_iob(start, end, rep_tok, ent_type, unk_tokens))
df.tagged_iob = df.tagged_iob.apply(eval)

# Create sub dataframes based on unique ids
unique_id = df["id"].unique().tolist()
tot = []
for uni_id in unique_id:
    df_sub = df[df["id"] == uni_id]
    iob_arr = df_sub.tagged_iob.tolist()

    # create only "O" tag array same length as iob tagged array
    if len(iob_arr) > 0:
        ans = []
        for i in iob_arr[0]:
            ans.append("O")

        # uniting all IOB tagged arrays as one array
        for ele in iob_arr:
            ans = unite_iob(ans, ele)

        tot.append((df_sub["id"].values[0], df_sub["reports"].values[0],
                    df_sub["report_tokenized"].values[0],
                    df_sub["unk_tokens"].values[0], ans))

#Create IOB tag included dataframe
df_result = pd.DataFrame(
    tot,
    columns=["id", "report", "tokenized_report", "diff_unk", "IOB_report"])

# extracting actual entities from IOB tags to check if it is correct or not
for idx, row in df_result.iterrows():
    ans = []
    for idx2, ele in enumerate(row.IOB_report):
        mini = []

        if ele.startswith("B"):
            count = idx2
            while count <= len(row.IOB_report) - 2:
                mini.append(count)
                count += 1
                if row.IOB_report[count] == "O" or row.IOB_report[
                        count].startswith("B"):
                    break
        if mini != []:
            ans.append(mini)

    final_ans = []
    for a in ans:
        entity = "".join(row.tokenized_report[a[0]:a[-1] + 1])
        final_ans.append(entity)

    df_result.loc[idx, "actual_ent"] = str(final_ans)

# data output path
path_out = Path.cwd() / "./"
os.makedirs(path_out, exist_ok=True)

# Change the filename based on label type
# file_name = "corpus517_entity_ext_iob.xlsx"
file_name = "58k_relation_iob_test.xlsx"
# file_name = "corpus517_relation_ann_iob.xlsx"

path_out = path_out.joinpath(file_name)
df_result.to_excel(path_out)

print("after IOB shape:", df_result.shape)