
def run_latch_same_phase_test(latch_graph) -> int:
    """
    iterate each edge of each node to
    check that each node must fanout or
    fanin to adjacent latch different clock
    phase.
    """

    print("[TWOCOLOR] Running same phase test...\n")
    
    error_count = 0
    for node in latch_graph.nodes.values():
        for fanout_node in node.fanout:
            if fanout_node.clock != node.clock:
                continue
            else:
                error_count += 1
    if error_count > 0:
        print(f"[TWOCOLOR] Counted {error_count} failed tests.")
        return error_count

    return error_count

def run_all_tests(latch_graph):

    print("[TWOCOLOR] Running all tests...\n")

    latch_check = run_latch_same_phase_test(latch_graph)

    if latch_check > 0:
        print("[TWOCOLOR] Test Suite Failed.")
    else:
        print(f"[TWOCOLOR] Latch checking report {latch_check} errors.")