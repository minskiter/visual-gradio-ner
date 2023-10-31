from typing import List, Tuple


def convert_bmes_to_span(labels: List[str]) -> List[Tuple[int, int, str]]:
    """
    convert BMES labels to (l,r,label), the interval includes the endpoint r. -> [l,r]

    Args:
        labels (List[str]): ["B-label","M-label","E-label"]

    Returns:
        List[Tuple[int,int,str]]: (l,r,label)
    """
    if len(labels) == 0:
        return []
    spans = []
    span = [-1, -1, "O"]
    labels.append("O")
    for i, label in enumerate(labels):
        if label[0] == "B" or label[0] == "S" or label[0] == "O":
            if span[0] != -1 and span[1] != -1:
                spans.append(tuple(span))
            span = [-1, -1, "O"]
        if label[0] == "B":
            span = [i, i, labels[i][2:]]
        elif label[0] == "S":
            spans.append((i, i, labels[i][2:]))
            span = [-1, -1, "O"]
        elif label[0] == "E" or label[0] == "I" or label[0] == "M":
            span[1] = i
    labels.pop()
    return spans
