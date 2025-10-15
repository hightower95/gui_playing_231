def merge_lists_preserve_order(list1, list2):
    seen = set()
    result = []

    # Add items from list1 in order
    for item in list1:
        if item not in seen:
            result.append(item)
            seen.add(item)

    # Add items from list2 that aren't already in result
    for item in list2:
        if item not in seen:
            result.append(item)
            seen.add(item)

    return result


# Example usage
list1 = ["CB1", "SH1", "SH2"]
list1 = ["CB1", "SH1", "SH2"]
list2 = ["CB1", "SH2", "SH4"]
merged = merge_lists_preserve_order(list1, list2)
print(merged)  # Output: ['CB1', 'SH1', 'SH2', 'SH4']
