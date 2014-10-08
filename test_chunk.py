def chunk_mates(chunks, tid):
    mates = []
    for chunk in chunks:
        if tid in chunk:
            mates = [0] + chunk[:]
            mates.remove(tid)
            break
    return mates

def non_chunk_mates(sent, chunks, tid):
    mates = []
    exclude = set()
    for chunk in chunks:
        if tid in chunk:
            exclude = set(chunk)
            break
    return list(set(sent) - exclude)

def non_chunk_mates(sent, chunks, tid):
    for chunk in chunks:
        if tid in chunk:
            current_chunk = chunk
            break
    return [t for t in range(len(sent)) if t not in current_chunk]

def devide(sent, chunks):
    chunk_tokens = []
    for chunk in chunks:
        if len(chunk) > 1:
            chunk_tokens += chunk
    chunk_tokens = sum([c for c in chunks if len(c) > 1], [])

    non_head_chunk_tokens = []
    for chunk in chunks:
        non_head_chunk_tokens += [d for d in chunk if sent[d].head in chunk]

    # out_tokens = list(set(range(1, len(sent))) - set(non_head_chunk_tokens))
    out_tokens = [t for t in range(1, len(sent)) if t not in non_head_chunk_tokens]
    return chunk_tokens, out_tokens


class Token():
    def __init__(self, id, head):
        self.head = head
        self.id = id

if __name__ == '__main__':
    sent = [Token(0, -1), Token(1,2), Token(2,3), Token(3,0), Token(4,5), Token(5,3), Token(6,3)]
    chunks = [[1,2], [3], [4,5], [6]]
    print chunks
    print devide(sent, chunks)
    print chunk_mates(chunks, 2)
    print non_chunk_mates(sent, chunks, 2)