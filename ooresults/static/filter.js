function filter_table(id, sel, filter) {
    var a, b, c, i, ii, iii, hit, h1, h2, f;
    f = filter.toUpperCase().normalize('NFD').replace(/[^\x00-\x7F]/g, '');
    a = document.getElementById(id);
    b = a.querySelectorAll(sel);
    h1 = null;
    hit1 = 0;
    for (ii = 1; ii < b.length; ii++) {
        if (b[ii].classList.contains("h1")) {
            if (h1 != null) {
                if (hit1 > 0) {
                    h1.style.display = "";
                } else {
                    h1.style.display = "none";
                }
            }
            h1 = b[ii];
            hit1 = 0;
        } else {
            hit = 0;
            if (b[ii].innerText.toUpperCase().normalize('NFD').replace(/[^\x00-\x7F]/g, '').indexOf(f) > -1) {
                hit = 1;
            }
            c = b[ii].getElementsByTagName("*");
            for (iii = 0; iii < c.length; iii++) {
                if (c[iii].innerText.toUpperCase().normalize('NFD').replace(/[^\x00-\x7F]/g, '').indexOf(f) > -1) {
                    hit = 1;
                }
            }
            if (hit == 1) {
                b[ii].style.display = "";
                hit1 += 1;
            } else {
                b[ii].style.display = "none";
            }
        }
    };
    if (h1 != null) {
        if (hit1 > 0) {
            h1.style.display = "";
        } else {
            h1.style.display = "none";
        }
    };
};
