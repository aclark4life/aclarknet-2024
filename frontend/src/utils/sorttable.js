// ==============================================================
// |                  This code was generated                   |
// |                   by ChatGPT, an OpenAI                    |
// |                      language model.                       |
// ==============================================================

const table = document.getElementById("table-select");
if (table) {
  const tbody = table.getElementsByTagName("tbody")[0];
  const rows = Array.from(tbody.getElementsByTagName("tr"));

  const sortTable = (columnIndex, ascending) => {
    const isNumeric = !isNaN(
      rows[0].getElementsByTagName("td")[columnIndex].textContent
    );
    rows.sort((row1, row2) => {
      const cell1 = row1.getElementsByTagName("td")[columnIndex].textContent;
      const cell2 = row2.getElementsByTagName("td")[columnIndex].textContent;
      const value1 = isNumeric ? parseInt(cell1) : cell1.toLowerCase();
      const value2 = isNumeric ? parseInt(cell2) : cell2.toLowerCase();
      if (value1 < value2) return ascending ? -1 : 1;
      if (value1 > value2) return ascending ? 1 : -1;
      return 0;
    });
    rows.forEach((row) => tbody.appendChild(row));
  };

  const addHeaderListeners = () => {
    const headers = table.getElementsByTagName("th");
    Array.from(headers).forEach((header, index) => {
      if (!header.classList.contains("no-sort")) {
        header.addEventListener("click", () => {
          const isAscending = header.getAttribute("data-order") === "asc";
          sortTable(index, !isAscending);
          header.setAttribute("data-order", isAscending ? "desc" : "asc");
        });
      }
    });
  };
  addHeaderListeners();
}
