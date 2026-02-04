(function () {
  var input = document.getElementById("searchInput");
  var table = document.getElementById("pegawaiTable");
  if (!input || !table) return;

  function searchTable() {
    var filter = input.value.toUpperCase();
    var tr = table.getElementsByTagName("tr");
    for (var i = 1; i < tr.length; i++) {
      var tdName = tr[i].getElementsByTagName("td")[2];
      var tdRole = tr[i].getElementsByTagName("td")[4];
      if (tdName || tdRole) {
        var txtName = tdName ? (tdName.textContent || tdName.innerText) : "";
        var txtRole = tdRole ? (tdRole.textContent || tdRole.innerText) : "";
        if (txtName.toUpperCase().indexOf(filter) > -1 || txtRole.toUpperCase().indexOf(filter) > -1) {
          tr[i].style.display = "";
        } else {
          tr[i].style.display = "none";
        }
      }
    }
  }

  input.addEventListener("keyup", searchTable);
})();
