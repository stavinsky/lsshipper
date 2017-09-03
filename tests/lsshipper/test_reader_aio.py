import pytest
from lsshipper.reader_aio import FileReader

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
    reader = FileReader(file1, sep=b"\n")
    lines = list()
    async for line, offset in reader.get_line(chunk_size=chunk_size):
        lines.append(line)
    assert lines[-1] is None
    lines = lines[:-1]
    with open(file1, "rb") as f:
        lines_orig = f.read().split(b"\n")
        if lines_orig[-1] == b"":
            lines_orig = lines_orig[:-1]
            # I'm doing like this because
            # I need to collect only strings with "\n" symbol at the end

    for i in range(len(lines)):
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
    reader = FileReader(file2, sep=b"\n")
    lines = list()
    async for line, offset in reader.get_line(chunk_size=chunk_size):
        lines.append(line)
    assert lines[-1] is None
    lines = lines[:-1]
    with open(file2, "rb") as f:
        lines_orig = f.read().split(b"\n")
        if 0 == lines_orig[-1][-1]:
            lines_orig = lines_orig[:-1]
            # I'm doing like this because
            # I need to collect only strings with "\n" symbol at the end
            # and we don't need any \x00
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
    reader = FileReader(file1, sep=b"\n")
    offsets = list()
    async for line, offset in reader.get_line(chunk_size=chunk_size):
        if line is not None:
            offsets.append(offset)

    with open(file1, "rb") as f:
        file_orig = f.read()
    offsets_orig = list(
        [offset + 1 for offset, ch in enumerate(file_orig)
         if bytes([ch]) == b'\n']
    )
    assert offsets == offsets_orig
