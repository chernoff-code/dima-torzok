def stack_repeated_segments(segments, phrase_repeat_threshold=5):
    """
    Group consecutive segments with identical text into one block.
    Only applies if repetitions reach the threshold (default 5).
    """
    stacked = []
    buffer = []
    prev_text = None

    for seg in segments:
        text = seg["text"].strip()

        if text == prev_text:
            buffer.append(seg)
        else:
            if len(buffer) >= phrase_repeat_threshold:
                stacked.append({
                    "start": buffer[0]["start"],
                    "end": buffer[-1]["end"],
                    "text": prev_text
                })
            elif buffer:
                stacked.extend(buffer)

            buffer = [seg]
            prev_text = text

    # Handle final buffer
    if len(buffer) >= phrase_repeat_threshold:
        stacked.append({
            "start": buffer[0]["start"],
            "end": buffer[-1]["end"],
            "text": prev_text
        })
    else:
        stacked.extend(buffer)

    return stacked
