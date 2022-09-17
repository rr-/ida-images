from librgb.reader import Reader

# Avoid complaints from __init__.py for CLI
try:
    import idaapi
    import idc
except ImportError:
    pass


class MemoryRange(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def length(self):
        return self.end - self.start

    def __str__(self):
        return "start: %08x end: %08x" % (self.start, self.end)


# Reads continuous memory chunk even if it spans accross multiple segments.
# "Missing" bytes are filled with NULL byte.
class MemoryReader(Reader):
    def __init__(self):
        super(MemoryReader, self).__init__()

    def get_padded_bytes(self, size):
        result = b"\x00" * size
        ranges_left = [MemoryRange(self.address, self.address + size)]

        segment_count = idaapi.get_segm_qty()
        valid_memory_ranges = []
        for i in range(segment_count):
            segment = idaapi.getnseg(i)
            # Skip segments with unstable data
            if segment.type == idaapi.SEG_XTRN:
                continue
            valid_memory_ranges.append(
                MemoryRange(segment.start_ea, segment.end_ea)
            )

        while len(ranges_left) > 0:
            # Get a requested memory range and remove it from the list
            current_range = ranges_left.pop()

            intersection = None
            for memory_range in valid_memory_ranges:
                start = max(current_range.start, memory_range.start)
                end = min(current_range.end, memory_range.end)
                if end > start:
                    intersection = MemoryRange(start, end)
                    break

            # No segment can satisfy any part of requested range
            if intersection is None:
                continue

            chunk = idc.get_bytes(
                intersection.start, intersection.end - intersection.start
            )
            if chunk is None:
                print(
                    "[librgb] Some bytes are unreadable in %s..%s"
                    % (
                        idc.atoa(intersection.start),
                        idc.atoa(intersection.end),
                    )
                )
                continue

            result = (
                result[0 : intersection.start - self.address]
                + chunk
                + result[intersection.end - self.address :]
            )
            assert len(result) == size

            # If necessary, enqueue ranges unsatisfied by chosen mem segment
            range1 = MemoryRange(current_range.start, intersection.start)
            range2 = MemoryRange(intersection.end, current_range.end)
            if range1.length() > 0:
                ranges_left.append(range1)
            if range2.length() > 0:
                ranges_left.append(range2)

        assert len(result) == size
        return result

    @property
    def min_address(self):
        return idaapi.cvar.inf.minEA

    @property
    def max_address(self):
        return idaapi.cvar.inf.maxEA

    @property
    def address_text(self):
        return idc.atoa(self.address)
