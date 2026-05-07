from payjoin_detector.core.heuristic import Heuristic, HeuristicResult
from payjoin_detector.core.transaction import Transaction


class UnionFind:
    """Lightweight Union-Find"""

    def __init__(self) -> None:
        self._parent: dict[str, str] = {}

    def _make(self, x: str) -> None:
        if x not in self._parent:
            self._parent[x] = x

    def find(self, x: str) -> str:
        self._make(x)
        while self._parent[x] != x:
            self._parent[x] = self._parent[self._parent[x]]
            x = self._parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self._parent[rb] = ra


class ClusteringHeuristic(Heuristic):
    name = "Clustering heuristic"

    def __init__(self, cluster_transactions: list[Transaction]) -> None:
        self.cluster_transactions = cluster_transactions

    def check(self, tx: Transaction) -> HeuristicResult:
        input_addresses = [
            inp.prevout.scriptpubkey_address
            for inp in tx.inputs
            if inp.prevout and inp.prevout.scriptpubkey_address
        ]

        if len(input_addresses) < 2:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal="fewer than 2 input addresses — clustering not applicable",
                html_signal="—"
            )
        uf = UnionFind()

        # Apply CIOH to all pre-fetched transactions
        for txn in self.cluster_transactions:
            self._apply_cioh(txn, uf)

        roots = {uf.find(addr) for addr in input_addresses}
        n_clusters = len(roots)

        if n_clusters == 1:
            return HeuristicResult(
                name=self.name,
                score=-2.0,
                signal=(
                    f"all {len(input_addresses)} input addresses belong to the same cluster"
                ),
                html_signal="Single cluster"
            )
        else:
            return HeuristicResult(
                name=self.name,
                score=0.0,
                signal=(f"input addresses span {n_clusters} distinct clusters"),
                html_signal=f"{n_clusters} separate clusters"
            )

    def _apply_cioh(self, txn: Transaction, uf: UnionFind) -> None:
        addrs = [
            inp.prevout.scriptpubkey_address
            for inp in txn.inputs
            if inp.prevout and inp.prevout.scriptpubkey_address
        ]

        if not addrs:
            return

        for addr in addrs[1:]:
            uf.union(addrs[0], addr)
