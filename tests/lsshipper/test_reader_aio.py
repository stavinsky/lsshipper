import pytest
from lsshipper.reader_aio import get_line

file1 = "tests/lsshipper/test_files/test1.txt"
file2 = "tests/lsshipper/test_files/test2.txt"


@pytest.mark.asyncio
@pytest.mark.parametrize("chunk_size", [
    (5),
    (128),
    (8129),
])
async def test_read_common_file(chunk_size):
    """Test on common file"""
    lines = list()
    async for line, offset in get_line(
            file1, sep=b'\n', chunk_size=chunk_size):
        lines.append(line)
    with open(file1, "rb") as f:
        lines_orig = f.read().split(b"\n")
        if lines_orig[-1] == b"":
            lines_orig = lines_orig[:-1]
            # I'm doing like this because
            # I need to collect only strings with "\n" symbol at the end
    assert len(lines) == len(lines_orig)
    for i in range(len(lines_orig)):
        assert lines[i] == lines_orig[i]

    assert lines == lines_orig


@pytest.mark.asyncio
@pytest.mark.parametrize("chunk_size", [
    (5),
    (128),
    (8129),
])
async def test_read_file_with_zeroes(chunk_size):
    """Test on file with zeroes at the
    end like MetaTrader Server main log file"""
    lines = list()
    async for line, offset in get_line(
            file2, sep=b'\n', chunk_size=chunk_size):
        lines.append(line)
    with open(file2, "rb") as f:
        lines_orig = f.read().split(b"\n")
        if 0 == lines_orig[-1][-1]:
            lines_orig = lines_orig[:-1]
            # I'm doing like this because
            # I need to collect only strings with "\n" symbol at the end
            # and we don't need any \x00
    assert len(lines) == len(lines_orig)
    for i in range(len(lines)):
        assert lines[i] == lines_orig[i]
    assert len(lines) == len(lines_orig)
    assert lines == lines_orig


@pytest.mark.asyncio
@pytest.mark.parametrize("chunk_size", [
    (5),
    (128),
    (8129),
])
async def test_offsets(chunk_size):
    """Test check offsets"""
    offsets = list()
    async for line, offset in get_line(
            file2, sep=b'\n', chunk_size=chunk_size):
        offsets.append(offset)

    with open(file2, "rb") as f:
        file_orig = f.read()
    offsets_orig = list(
        [offset + 1 for offset, ch in enumerate(file_orig)
         if bytes([ch]) == b'\n']
    )
    assert offsets == offsets_orig
