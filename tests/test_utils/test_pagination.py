
# from app.utils.pagination import paginate
# def test_pagination():
#     assert paginate([], 1, 10) == []
#     assert paginate([1, 2, 3], 1, 10) == [1, 2, 3]
#     assert paginate([1, 2, 3], 1, 2) == [1, 2]
#     assert paginate([1, 2, 3], 2, 2) == [3]
#     assert paginate([1, 2, 3], 3, 1) == []
def paginate(items, page, page_size):
    """Paginate a list of items."""
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end]