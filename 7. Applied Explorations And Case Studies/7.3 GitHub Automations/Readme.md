# GitHub Bulk Upload Engine – Skills & Thought Process

## 1. Problem Framing

Goal:
Upload a large number of local files to a GitHub repository.

Constraints:

* GitHub API is rate-limited
* Commits must be sequential (linear history)
* Large batches cause failures or throttling
* One-file-per-commit is too slow if done naïvely

Core tension:

* Granularity (1 file = 1 commit)
* Throughput (minimize API overhead)

---

## 2. Mental Model of Git (Critical Insight)

Git is not file-based. It is snapshot-based.

Each commit consists of:

* Tree (snapshot of file structure)
* Parent commit
* Metadata

Pipeline:

```
FILE → BLOB → TREE → COMMIT → REF UPDATE
```

Key implication:

* You do not "add a file"
* You create a new snapshot that includes that file

---

## 3. API Decomposition

Each file requires:

1. `create_blob`
   Converts file content → Git object

2. `create_tree`
   Builds new snapshot using previous tree + new blob

3. `create_commit`
   Links new tree to parent commit

4. `update_ref`
   Moves branch pointer to new commit

Bottleneck:

* `update_ref` is the slowest and most restricted step

---

## 4. Optimization Strategy

### Naïve Approach

```
1 file → 1 commit → 1 ref update
```

Problems:

* Too many network calls
* Hits rate limits quickly
* Extremely slow

---

### Batch Approach

```
500 files → 1 commit
```

Problems:

* Loses per-file history
* Large payload risks
* Hard to debug

---

### Hybrid Chain Approach (Chosen)

```
N files → N commits → 1 ref update
```

Mechanism:

* Build commit chain locally
* Push only final commit

Example:

```
HEAD → C1 → C2 → C3 → ... → C10
```

Only:

```
update_ref(C10)
```

Benefits:

* Maintains per-file commit history
* Reduces branch updates
* Avoids rate limits

---

## 5. Execution Flow

### Step 1: Initialization

```
parent = head_sha()
base_tree = tree_sha(parent)
```

This anchors the system to current repo state.

---

### Step 2: Process Files in Chunks

Chunk size:

```
CHAIN_SIZE = 10
```

Reason:

* Balance between speed and stability
* Avoid large payload failures

---

### Step 3: For Each File

```
blob = create_blob(file)
tree = create_tree(previous_tree + blob)
commit = create_commit(parent, tree)
```

Update pointers:

```
parent = commit
tree = new_tree
```

This builds a linear chain.

---

### Step 4: Push Chain

```
update_ref(last_commit)
```

Only one branch update per chunk.

---

### Step 5: Advance Global State

```
parent = last_commit
base_tree = last_tree
```

Next batch builds on updated repo state.

---

## 6. Error Handling Philosophy

Principles:

* Fail loudly
* Do not silently skip API errors
* Preserve forward progress

Key guard:

```
if last_commit is None:
    skip update_ref
```

Prevents crash when entire batch fails.

---

## 7. Rate Limit Strategy

GitHub enforces:

* Primary rate limits
* Secondary (burst) limits

Mitigation:

```
time.sleep(0.5)
```

Counterintuitive:

* Slowing down slightly increases total throughput

---

## 8. Performance Characteristics

Per file:

* 3 API calls (blob, tree, commit)

Per batch:

* 1 ref update

Approximate throughput:

* 1–3 files/sec depending on network

Scaling:

| Mode            | Speed     |
| --------------- | --------- |
| Per-file commit | Very slow |
| Hybrid chain    | Balanced  |
| Batch commit    | Fastest   |

---

## 9. Design Tradeoffs

### Pros

* Clean commit history
* Scalable for large datasets
* Avoids API abuse patterns

### Cons

* Still network-bound
* Cannot parallelize commits
* Slight complexity in chaining

---

## 10. Extensibility Ideas

### Parallel Blob Preprocessing

* Precompute blobs concurrently
* Feed into sequential commit pipeline

### Checkpointing

* Track uploaded files
* Resume safely after failure

### Deduplication

* Hash content
* Skip identical blobs

---

## 11. Core Engineering Lessons

1. Bottlenecks are rarely where you expect
   → commits, not uploads

2. Systems thinking beats brute force
   → reduce expensive operations, not total work

3. APIs encode constraints
   → design must adapt to them

4. Sequential constraints kill parallelism
   → commit chain must remain linear

5. Perception vs reality
   → "file upload" is actually "graph mutation"

---

## 12. Final Mental Model

You are not uploading files.

You are constructing a **directed acyclic graph of commits**, one node at a time, and periodically telling GitHub:

```
"this is now the new reality"
```

Everything else is implementation detail.

