
//  Persian Date By Saeed Auditore (Saeed.auditore@yahoo.com)
//
//
//  DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
//                      Version 2, December 2004 
//
//   Copyright (C) 2004 Sam Hocevar <sam@hocevar.net> 
//
//   Everyone is permitted to copy and distribute verbatim or modified 
//   copies of this license document, and changing it is allowed as long 
//   as the name is changed. 
//
//              DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
//     TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION 
//
//    0. You just DO WHAT THE FUCK YOU WANT TO.



Date.g_days_in_month=[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
Date.j_days_in_month= [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29];
Date.PersianToGregorian = function(j_y, j_m, j_d)
{
    j_y = parseInt(j_y);
    j_m = parseInt(j_m);
    j_d = parseInt(j_d);
    var jy = j_y-979;
    var jm = j_m-1;
    var jd = j_d-1;

    var j_day_no = 365*jy + (parseInt(jy / 33)*8) + parseInt((jy%33+3) / 4);
    for (var i=0; i < jm; ++i) j_day_no += Date.j_days_in_month[i];

    j_day_no += jd;

    var g_day_no = j_day_no+79;

    var gy = 1600 + 400 * parseInt(g_day_no / 146097); /* 146097 = 365*400 + 400/4 - 400/100 + 400/400 */
    g_day_no = g_day_no % 146097;

    var leap = true;
    if (g_day_no >= 36525) /* 36525 = 365*100 + 100/4 */
    {
        g_day_no--;
        gy += 100*parseInt(g_day_no/  36524); /* 36524 = 365*100 + 100/4 - 100/100 */
        g_day_no = g_day_no % 36524;

        if (g_day_no >= 365)
            g_day_no++;
        else
            leap = false;
    }

    gy += 4*parseInt(g_day_no/ 1461); /* 1461 = 365*4 + 4/4 */
    g_day_no %= 1461;

    if (g_day_no >= 366) {
        leap = false;

        g_day_no--;
        gy += parseInt(g_day_no/ 365);
        g_day_no = g_day_no % 365;
    }

    for (var i = 0; g_day_no >= Date.g_days_in_month[i] + (i == 1 && leap); i++)
        g_day_no -= Date.g_days_in_month[i] + (i == 1 && leap);
    var gm = i+1;
    var gd = g_day_no+1;

    return [gy, gm, gd];
};
Date.GregorianToPersian = function(g_y, g_m, g_d)
{
    g_y = parseInt(g_y);
    g_m = parseInt(g_m);
    g_d = parseInt(g_d);
    var gy = g_y-1600;
    var gm = g_m-1;
    var gd = g_d-1;

    var g_day_no = 365*gy+parseInt((gy+3) / 4)-parseInt((gy+99)/100)+parseInt((gy+399)/400);

    for (var i=0; i < gm; ++i)
    g_day_no += Date.g_days_in_month[i];
    if (gm>1 && ((gy%4==0 && gy%100!=0) || (gy%400==0)))
    /* leap and after Feb */
    ++g_day_no;
    g_day_no += gd;

    var j_day_no = g_day_no-79;

    var j_np = parseInt(j_day_no/ 12053);
    j_day_no %= 12053;

    var jy = 979+33*j_np+4*parseInt(j_day_no/1461);

    j_day_no %= 1461;

    if (j_day_no >= 366) {
        jy += parseInt((j_day_no-1)/ 365);
        j_day_no = (j_day_no-1)%365;
    }

    for (var i = 0; i < 11 && j_day_no >= Date.j_days_in_month[i]; ++i) {
        j_day_no -= Date.j_days_in_month[i];
    }
    var jm = i+1;
    var jd = j_day_no+1;


    return [jy, jm, jd];
};
function xf(format) {
    var args = Array.prototype.slice.call(arguments, 1);
    return format.replace(/\{(\d+)\}/g, function(m, i) {
        return args[i];
    });
}
Date.PcheckDate = function(j_y, j_m, j_d)
{
    return !(j_y < 0 || j_y > 32767 || j_m < 1 || j_m > 12 || j_d < 1 || j_d >
        (Date.j_days_in_month[j_m-1] + (j_m == 12 && !((j_y-979)%33%4))));
}

Date.PformatCodeToRegex = function(character, currentGroup) {
    // Note: currentGroup - position in regex result array (see notes for Date.parseCodes below)
    var p = Date.PparseCodes[character];

    if (p) {
      p = typeof p == 'function'? p() : p;
      Date.PparseCodes[character] = p; // reassign function result to prevent repeated execution
    }

    return p? Ext.applyIf({
      c: p.c? xf(p.c, currentGroup || "{0}") : p.c
    }, p) : {
        g:0,
        c:null,
        s:Ext.escapeRe(character) // treat unrecognised characters as literals
    }
}




var $Pf = Date.PformatCodeToRegex;
Date.prototype.setPFullYear = function(y, m, d) {
                var gd = this.getDate();
                var gm = this.getMonth();
                var gy = this.getFullYear();
                var j = Date.GregorianToPersian(gy, gm+1, gd);
                if (y < 100) y += 1300;
                j[0] = y;
                if (m != undefined) {
                    if (m > 11) {
                        j[0] += Math.floor(m / 12);
                        m = m % 12;
                    }
                    j[1] = m + 1;
                }
                if (d != undefined) j[2] = d;
                var g = Date.PersianToGregorian(j[0], j[1], j[2]);
                return this.setFullYear(g[0], g[1]-1, g[2]);
            }
Date.prototype.setPMonth = function(m, d) {
                var gd = this.getDate();
                var gm = this.getMonth();
                var gy = this.getFullYear();
                var j = Date.GregorianToPersian(gy, gm+1, gd);
                if (m > 11) {
                    j[0] += math.floor(m / 12);
                    m = m % 12;
                }
                j[1] = m+1;
                if (d != undefined) j[2] = d;
                var g = Date.PersianToGregorian(j[0], j[1], j[2]);
                return this.setFullYear(g[0], g[1]-1, g[2]);
            }
Date.prototype.setPDate = function(d) {
                var gd = this.getDate();
                var gm = this.getMonth();
                var gy = this.getFullYear();
                var j = Date.GregorianToPersian(gy, gm+1, gd);
                j[2] = d;
                var g = Date.PersianToGregorian(j[0], j[1], j[2]);
                return this.setFullYear(g[0], g[1]-1, g[2]);
            }
Date.prototype.getPFullYear = function() {
                var gd = this.getDate();
                var gm = this.getMonth();
                var gy = this.getFullYear();
                var j = Date.GregorianToPersian(gy, gm+1, gd);
                return j[0];
            };
Date.prototype.getPMonth = function() {
                        var gd = this.getDate();
                        var gm = this.getMonth();
                        var gy = this.getFullYear();
                        var j = Date.GregorianToPersian(gy, gm+1, gd);
                        return j[1]-1;
                    };
Date.prototype.getPDate = function() {
    // console.log(this);
                        var gd = this.getDate();
                        var gm = this.getMonth();
                        var gy = this.getFullYear();
                        var j = Date.GregorianToPersian(gy, gm+1, gd);
                        return j[2];
                    };
Date.prototype.getPDay = function() {
    var day = this.getDay();
    day = (day + 1) % 7;
    return day;
                    };
    
    /**
     * Persian UTC functions 
     */
    
Date.prototype.settPUTCFullYear = function(y, m, d) {
                        var gd = this.getUTCDate();
                        var gm = this.getUTCMonth();
                        var gy = this.getUTCFullYear();
                        var j = Date.GregorianToPersian(gy, gm+1, gd);
                        if (y < 100) y += 1300;
                        j[0] = y;
                        if (m != undefined) {
                            if (m > 11) {
                                j[0] += Math.floor(m / 12);
                                m = m % 12;
                            }
                            j[1] = m + 1;
                        }
                        if (d != undefined) j[2] = d;
                        var g = Date.GregorianToPersian(j[0], j[1], j[2]);
                        return this.setUTCFullYear(g[0], g[1]-1, g[2]);
                    }
Date.prototype.settPUTCMonth = function(m, d) {
                        var gd = this.getUTCDate();
                        var gm = this.getUTCMonth();
                        var gy = this.getUTCFullYear();
                        var j = Date.GregorianToPersian(gy, gm+1, gd);
                        if (m > 11) {
                            j[0] += math.floor(m / 12);
                            m = m % 12;
                        }
                        j[1] = m+1;
                        if (d != undefined) j[2] = d;
                        var g = Date.GregorianToPersian(j[0], j[1], j[2]);
                        return this.setUTCFullYear(g[0], g[1]-1, g[2]);
                    }
Date.prototype.setPUTCDate = function(d) {
                var gd = this.getUTCDate();
                var gm = this.getUTCMonth();
                var gy = this.getUTCFullYear();
                var j = Date.GregorianToPersian(gy, gm+1, gd);
                j[2] = d;
                var g = Date.PersianToGregorian(j[0], j[1], j[2]);
                return this.setFullYear(g[0], g[1]-1, g[2]);
            }
Date.prototype.getPUTCFullYear = function() {
                var gd = this.getUTCDate();
                var gm = this.getUTCMonth();
                var gy = this.getUTCFullYear();
                var j = Date.GregorianToPersian(gy, gm+1, gd);
                return j[0];
            }
Date.prototype.getPUTCMonth = function() {
                        var gd = this.getUTCDate();
                        var gm = this.getUTCMonth();
                        var gy = this.getUTCFullYear();
                        var j = Date.GregorianToPersian(gy, gm+1, gd);
                        return j[1]-1;
                    }
Date.prototype.getPUTCMonth = function() {
                        var gd = this.getUTCDate();
                        var gm = this.getUTCMonth();
                        var gy = this.getUTCFullYear();
                        var j = Date.GregorianToPersian(gy, gm+1, gd);
                        return j[1]-1;
                    }
Date.prototype.getPUTCDate = function() {
                        var gd = this.getUTCDate();
                        var gm = this.getUTCMonth();
                        var gy = this.getUTCFullYear();
                        var j = Date.GregorianToPersian(gy, gm+1, gd);
                        return j[2];
                    }
Date.prototype.getPUTCDay = function() {
                        var day = this.getUTCDay();
                        day = (day + 1) % 7;
                        return day;
                    }

Date.PmonthNames=[
        "Farvardin",
        "Ordibehesht",
        "Khordad",
        "Tir",
        "Mordad",
        "Sahrivar",
        "Mehr",
        "Aban",
        "Azar",
        "Dey",
        "Bahman",
        "Esfand"
    ];
Date.PmonthNumbers = {
        Far:0,
        Ord:1,
        Kho:2,
        Tir:3,
        Mor:4,
        Sha:5,
        Meh:6,
        Aba:7,
        Aza:8,
        Dey:9,
        Bah:10,
        Esf:11
    };

     /**
     * Get the short month name for the given month number in persian date.
     */
    Date.getPShortMonthName = function(month) {
        return Date.PmonthNames[month].substring(0, 3);
    }
    
     /**
     * Get the zero-based javascript month number for the given short/full month name in persian date.
     */
    Date.getPMonthNumber = function(name) {
        // handle camel casing for english month names (since the keys for the Date.monthNumbers hash are case sensitive)
        return Date.PmonthNumbers[name.substring(0, 1).toUpperCase() + name.substring(1, 3).toLowerCase()];
    };
    Date.PformatCodes = {
        d: "String.leftPad(this.getPDate(), 2, '0')",
        D: "Date.getPShortDayName(this.getDay())", // get localised short day name
        j: "this.getPDate()",
        l: "Date.dayNames[this.getPDay()]",
        N: "(this.getPDay() ? this.getPDay() : 7)",
        S: "this.getSuffix()",
        w: "this.getPDay()",
        z: "this.getPDayOfYear()",
        W: "String.leftPad(this.getPWeekOfYear(), 2, '0')",
        F: "Date.PmonthNames[this.getPMonth()]",
        m: "String.leftPad(this.getPMonth() + 1, 2, '0')",
        M: "Date.getPShortMonthName(this.getPMonth())", // get localised short month name
        n: "(this.getPMonth() + 1)",
        t: "this.getPDaysInMonth()",
        L: "(this.isKabiseYear() ? 1 : 0)",
        //Persian Date don't have ISO-8601 year number
        //o: "(this.getPFullYear() + (this.getPWeekOfYear() == 1 && this.getPMonth() > 0 ? +1 : (this.getPWeekOfYear() >= 52 && this.getPMonth() < 11 ? -1 : 0)))",
        Y: "this.getPFullYear()",
        y: "('' + this.getPFullYear()).substring(2, 4)",
        a: "(this.getHours() < 12 ? 'am' : 'pm')",
        A: "(this.getHours() < 12 ? 'AM' : 'PM')",
        g: "((this.getHours() % 12) ? this.getHours() % 12 : 12)",
        G: "this.getHours()",
        h: "String.leftPad((this.getHours() % 12) ? this.getHours() % 12 : 12, 2, '0')",
        H: "String.leftPad(this.getHours(), 2, '0')",
        i: "String.leftPad(this.getMinutes(), 2, '0')",
        s: "String.leftPad(this.getSeconds(), 2, '0')",
        u: "String.leftPad(this.getMilliseconds(), 3, '0')",
        O: "this.getGMTOffset()",
        P: "this.getGMTOffset(true)",
        T: "this.getTimezone()",
        Z: "(this.getTimezoneOffset() * -60)",

        c: function() { // ISO-8601 -- GMT format
            for (var c = "Y-m-dTH:i:sP", code = [], i = 0, l = c.length; i < l; ++i) {
                var e = c.charAt(i);
                code.push(e == "T" ? "'T'" : Date.getPFormatCode(e)); // treat T as a character literal
            }
            return code.join(" + ");
        },
        U: "Math.round(this.getTime() / 1000)"
    };

    /**
     * Checks if the passed Date parameters will cause a javascript Date "rollover".
     * @param {Number} year 4-digit year
     * @param {Number} month 1-based month-of-year
     * @param {Number} day Day of month
     * @param {Number} hour (optional) Hour
     * @param {Number} minute (optional) Minute
     * @param {Number} second (optional) Second
     * @param {Number} millisecond (optional) Millisecond
     * @return {Boolean} true if the passed parameters do not cause a Date "rollover", false otherwise.
     * @static
     */
    Date.isPValid = function(y, m, d, h, i, s, ms) {
        // setup defaults
        h = h || 0;
        i = i || 0;
        s = s || 0;
        ms = ms || 0;
        if(!Date.PcheckDate(y,m,d)) return false;
        g=Date.PersianToGregorian(y,m,d);
            y=g[0];
            m=g[1];
            d=g[2];
        var dt = new Date(y, m - 1, d, h, i, s, ms);

        return y == dt.getFullYear() &&
            m == dt.getMonth() + 1 &&
            d == dt.getDate() &&
            h == dt.getHours() &&
            i == dt.getMinutes() &&
            s == dt.getSeconds() &&
            ms == dt.getMilliseconds();
    }
    Date.PparseRegexes= [];
    Date.PparseDate = function(input, format, strict) {
        var p = Date.PparseFunctions;
    
        if (p[format] == null) {
            Date.PcreateParser(format);
        }
        return p[format](input, Ext.isDefined(strict) ? strict : Date.useStrict);
    }
    Date.getPFormatCode = function(character) {
        var f = Date.PformatCodes[character];

        if (f) {
          f = typeof f == 'function'? f() : f;
          Date.PformatCodes[character] = f; // reassign function result to prevent repeated execution
        }

        // note: unknown characters are treated as literals
        return f || ("'" + String.escape(character) + "'");
    }
    Date.PformatFunctions = {
        "M$": function() {
            // UTC milliseconds since Unix epoch (M$-AJAX serialized date format (MRSF))
            return '\\/Date(' + this.getTime() + ')\\/';
        }
    }
     // private
    Date.PcreateFormat = function(format) {
        var code = [],
            special = false,
            ch = '';

        for (var i = 0; i < format.length; ++i) {
            ch = format.charAt(i);
            if (!special && ch == "\\") {
                special = true;
            } else if (special) {
                special = false;
                code.push("'" + String.escape(ch) + "'");
            } else {
                code.push(Date.PgetFormatCode(ch))
            }
        }
        Date.PformatFunctions[format] = new Function("return " + code.join('+'));
    }
     // private
    Date.PgetFormatCode = function(character) {
        var f = Date.PformatCodes[character];

        if (f) {
          f = typeof f == 'function'? f() : f;
          Date.PformatCodes[character] = f; // reassign function result to prevent repeated execution
        }

        // note: unknown characters are treated as literals
        return f || ("'" + String.escape(character) + "'");
    }
    // private
    Date.PcreateParser = function() {
        var code = [
            "var dt, y, m, d, h, i, s, ms, o, z, zz, u, v,",
                "def = Date.defaults,",
                "results = String(input).match(Date.PparseRegexes[{0}]);", // either null, or an array of matched strings

            "if(results){",
                "{1}",

                "if(u != null){", // i.e. unix time is defined
                    "v = new Date(u * 1000);", // give top priority to UNIX time
                "}else{",
                    // create Date object representing midnight of the current day;
                    // this will provide us with our date defaults
                    // (note: clearTime() handles Daylight Saving Time automatically)
                    "dt = (new Date()).clearTime();",

                    // date calculations (note: these calculations create a dependency on Ext.num())
                    "y = y >= 0? y : Ext.num(def.y, dt.getPFullYear());",
                    "m = m >= 0? m : Ext.num(def.m - 1, dt.PgetMonth());",
                    "d = d >= 0? d : Ext.num(def.d, dt.PgetDate());",
                    "gm=Date.PersianToGregorian(y,m+1,d);y=gm[0];m=gm[1]-1;d=gm[2];",

                    // time calculations (note: these calculations create a dependency on Ext.num())
                    "h  = h || Ext.num(def.h, dt.getHours());",
                    "i  = i || Ext.num(def.i, dt.getMinutes());",
                    "s  = s || Ext.num(def.s, dt.getSeconds());",
                    "ms = ms || Ext.num(def.ms, dt.getMilliseconds());",

                    "if(z >= 0 && y >= 0){",
                        // both the year and zero-based day of year are defined and >= 0.
                        // these 2 values alone provide sufficient info to create a full date object

                        // create Date object representing January 1st for the given year
                        "v = new Date(y, 0, 1, h, i, s, ms);",

                        // then add day of year, checking for Date "rollover" if necessary
                        "v = !strict? v : (strict === true && (z <= 364 || (v.isLeapYear() && z <= 365))? v.add(Date.DAY, z) : null);",
                    "}else if(strict === true && !Date.isValid(y, m + 1, d, h, i, s, ms)){", // check for Date "rollover"
                        "v = null;", // invalid date, so return null
                    "}else{",
                        // plain old Date object
                        "v = new Date(y, m, d, h, i, s, ms);",
                    "}",
                "}",
            "}",

            "if(v){",
                // favour UTC offset over GMT offset
                "if(zz != null){",
                    // reset to UTC, then add offset
                    "v = v.add(Date.SECOND, -v.getTimezoneOffset() * 60 - zz);",
                "}else if(o){",
                    // reset to GMT, then add offset
                    "v = v.add(Date.MINUTE, -v.getTimezoneOffset() + (sn == '+'? -1 : 1) * (hr * 60 + mn));",
                "}",
            "}",

            "return v;"
        ].join('\n');

        return function(format) {
            var regexNum = Date.PparseRegexes.length,
                currentGroup = 1,
                calc = [],
                regex = [],
                special = false,
                ch = "";

            for (var i = 0; i < format.length; ++i) {
                ch = format.charAt(i);
                if (!special && ch == "\\") {
                    special = true;
                } else if (special) {
                    special = false;
                    regex.push(String.escape(ch));
                } else {
                    var obj = $Pf(ch, currentGroup);
                    currentGroup += obj.g;
                    regex.push(obj.s);
                    if (obj.g && obj.c) {
                        calc.push(obj.c);
                    }
                }
            }
            Date.PparseRegexes[regexNum] = new RegExp("^" + regex.join('') + "$", "i");
            Date.PparseFunctions[format] = new Function("input", "strict", xf(code, regexNum, calc.join('')));
        }
    }();
    Date.PparseFunctions = {
        "M$": function(input, strict) {
            // note: the timezone offset is ignored since the M$ Ajax server sends
            // a UTC milliseconds-since-Unix-epoch value (negative values are allowed)
            var re = new RegExp('\\/Date\\(([-+])?(\\d+)(?:[+-]\\d{4})?\\)\\/');
            var r = (input || '').match(re);
            return r? new Date(((r[1] || '') + r[2]) * 1) : null;
        }
    };
    Date.PparseCodes = {
        /*
         * Notes:
         * g = {Number} calculation group (0 or 1. only group 1 contributes to date calculations.)
         * c = {String} calculation method (required for group 1. null for group 0. {0} = currentGroup - position in regex result array)
         * s = {String} regex pattern. all matches are stored in results[], and are accessible by the calculation mapped to 'c'
         */
        d: {
            g:1,
            c:"d = parseInt(results[{0}], 10);\n",
            s:"(\\d{2})" // day of month with leading zeroes (01 - 31)
        },
        j: {
            g:1,
            c:"d = parseInt(results[{0}], 10);\n",
            s:"(\\d{1,2})" // day of month without leading zeroes (1 - 31)
        },
        D: function() {
            for (var a = [], i = 0; i < 7; a.push(Date.getShortDayName(i)), ++i); // get localised short day names
            return {
                g:0,
                c:null,
                s:"(?:" + a.join("|") +")"
            }
        },
        l: function() {
            return {
                g:0,
                c:null,
                s:"(?:" + Date.dayNames.join("|") + ")"
            }
        },
        N: {
            g:0,
            c:null,
            s:"[1-7]" // ISO-8601 day number (1 (monday) - 7 (sunday))
        },
        S: {
            g:0,
            c:null,
            s:"(?:st|nd|rd|th)"
        },
        w: {
            g:0,
            c:null,
            s:"[0-6]" // javascript day number (0 (sunday) - 6 (saturday))
        },
        z: {
            g:1,
            c:"z = parseInt(results[{0}], 10);\n",
            s:"(\\d{1,3})" // day of the year (0 - 364 (365 in leap years))
        },
        W: {
            g:0,
            c:null,
            s:"(?:\\d{2})" // ISO-8601 week number (with leading zero)
        },
        F: function() {
            return {
                g:1,
                c:"m = parseInt(Date.getPMonthNumber(results[{0}]), 10);\n", // get localised month number
                s:"(" + Date.PmonthNames.join("|") + ")"
            }
        },
        M: function() {
            for (var a = [], i = 0; i < 12; a.push(Date.getPShortMonthName(i)), ++i); // get localised short month names
            return Ext.applyIf({
                s:"(" + a.join("|") + ")"
            }, $f("F"));
        },
        m: {
            g:1,
            c:"m = parseInt(results[{0}], 10) - 1;\n",
            s:"(\\d{2})" // month number with leading zeros (01 - 12)
        },
        n: {
            g:1,
            c:"m = parseInt(results[{0}], 10) - 1;\n",
            s:"(\\d{1,2})" // month number without leading zeros (1 - 12)
        },
        t: {
            g:0,
            c:null,
            s:"(?:\\d{2})" // no. of days in the month (28 - 31)
        },
        L: {
            g:0,
            c:null,
            s:"(?:1|0)"
        },
        o: function() {
            return $Pf("Y");
        },
        Y: {
            g:1,
            c:"y = parseInt(results[{0}], 10);\n",
            s:"(\\d{4})" // 4-digit year
        },
        y: {
            g:1,
            c:"var ty = parseInt(results[{0}], 10);\n"
                + "y =  1300 + ty;\n", // 2-digit year
            s:"(\\d{1,2})"
        },
        a: {
            g:1,
            c:"if (results[{0}] == 'am') {\n"
                + "if (h == 12) { h = 0; }\n"
                + "} else { if (h < 12) { h += 12; }}",
            s:"(am|pm)"
        },
        A: {
            g:1,
            c:"if (results[{0}] == 'AM') {\n"
                + "if (h == 12) { h = 0; }\n"
                + "} else { if (h < 12) { h += 12; }}",
            s:"(AM|PM)"
        },
        g: function() {
            return $Pf("G");
        },
        G: {
            g:1,
            c:"h = parseInt(results[{0}], 10);\n",
            s:"(\\d{1,2})" // 24-hr format of an hour without leading zeroes (0 - 23)
        },
        h: function() {
            return $Pf("H");
        },
        H: {
            g:1,
            c:"h = parseInt(results[{0}], 10);\n",
            s:"(\\d{2})" //  24-hr format of an hour with leading zeroes (00 - 23)
        },
        i: {
            g:1,
            c:"i = parseInt(results[{0}], 10);\n",
            s:"(\\d{2})" // minutes with leading zeros (00 - 59)
        },
        s: {
            g:1,
            c:"s = parseInt(results[{0}], 10);\n",
            s:"(\\d{2})" // seconds with leading zeros (00 - 59)
        },
        u: {
            g:1,
            c:"ms = results[{0}]; ms = parseInt(ms, 10)/Math.pow(10, ms.length - 3);\n",
            s:"(\\d+)" // decimal fraction of a second (minimum = 1 digit, maximum = unlimited)
        },
        O: {
            g:1,
            c:[
                "o = results[{0}];",
                "var sn = o.substring(0,1),", // get + / - sign
                    "hr = o.substring(1,3)*1 + Math.floor(o.substring(3,5) / 60),", // get hours (performs minutes-to-hour conversion also, just in case)
                    "mn = o.substring(3,5) % 60;", // get minutes
                "o = ((-12 <= (hr*60 + mn)/60) && ((hr*60 + mn)/60 <= 14))? (sn + String.leftPad(hr, 2, '0') + String.leftPad(mn, 2, '0')) : null;\n" // -12hrs <= GMT offset <= 14hrs
            ].join("\n"),
            s: "([+\-]\\d{4})" // GMT offset in hrs and mins
        },
        P: {
            g:1,
            c:[
                "o = results[{0}];",
                "var sn = o.substring(0,1),", // get + / - sign
                    "hr = o.substring(1,3)*1 + Math.floor(o.substring(4,6) / 60),", // get hours (performs minutes-to-hour conversion also, just in case)
                    "mn = o.substring(4,6) % 60;", // get minutes
                "o = ((-12 <= (hr*60 + mn)/60) && ((hr*60 + mn)/60 <= 14))? (sn + String.leftPad(hr, 2, '0') + String.leftPad(mn, 2, '0')) : null;\n" // -12hrs <= GMT offset <= 14hrs
            ].join("\n"),
            s: "([+\-]\\d{2}:\\d{2})" // GMT offset in hrs and mins (with colon separator)
        },
        T: {
            g:0,
            c:null,
            s:"[A-Z]{1,4}" // timezone abbrev. may be between 1 - 4 chars
        },
        Z: {
            g:1,
            c:"zz = results[{0}] * 1;\n" // -43200 <= UTC offset <= 50400
                  + "zz = (-43200 <= zz && zz <= 50400)? zz : null;\n",
            s:"([+\-]?\\d{1,5})" // leading '+' sign is optional for UTC offset
        },
        c: function() {
            var calc = [],
                arr = [
                    $Pf("Y", 1), // year
                    $Pf("m", 2), // month
                    $Pf("d", 3), // day
                    $Pf("h", 4), // hour
                    $Pf("i", 5), // minute
                    $Pf("s", 6), // second
                    {c:"ms = results[7] || '0'; ms = parseInt(ms, 10)/Math.pow(10, ms.length - 3);\n"}, // decimal fraction of a second (minimum = 1 digit, maximum = unlimited)
                    {c:[ // allow either "Z" (i.e. UTC) or "-0530" or "+08:00" (i.e. UTC offset) timezone delimiters. assumes local timezone if no timezone is specified
                        "if(results[8]) {", // timezone specified
                            "if(results[8] == 'Z'){",
                                "zz = 0;", // UTC
                            "}else if (results[8].indexOf(':') > -1){",
                                $Pf("P", 8).c, // timezone offset with colon separator
                            "}else{",
                                $Pf("O", 8).c, // timezone offset without colon separator
                            "}",
                        "}"
                    ].join('\n')}
                ];

            for (var i = 0, l = arr.length; i < l; ++i) {
                calc.push(arr[i].c);
            }

            return {
                g:1,
                c:calc.join(""),
                s:[
                    arr[0].s, // year (required)
                    "(?:", "-", arr[1].s, // month (optional)
                        "(?:", "-", arr[2].s, // day (optional)
                            "(?:",
                                "(?:T| )?", // time delimiter -- either a "T" or a single blank space
                                arr[3].s, ":", arr[4].s,  // hour AND minute, delimited by a single colon (optional). MUST be preceded by either a "T" or a single blank space
                                "(?::", arr[5].s, ")?", // seconds (optional)
                                "(?:(?:\\.|,)(\\d+))?", // decimal fraction of a second (e.g. ",12345" or ".98765") (optional)
                                "(Z|(?:[-+]\\d{2}(?::)?\\d{2}))?", // "Z" (UTC) or "-0530" (UTC offset without colon delimiter) or "+08:00" (UTC offset with colon delimiter) (optional)
                            ")?",
                        ")?",
                    ")?"
                ].join("")
            }
        },
        U: {
            g:1,
            c:"u = parseInt(results[{0}], 10);\n",
            s:"(-?\\d+)" // leading minus sign indicates seconds before UNIX epoch
        }
    }
    // private
    Date.prototype.PdateFormat = function(format) {
        if (Date.PformatFunctions[format] == null) {
            Date.PcreateFormat(format);
        }
        return Date.PformatFunctions[format].call(this);
    }
    Date.prototype.getPDayOfYear = function() {
        var i = 0,
            num = 0,
            d = this,
            m = this.getPMonth();

        for (i = 0, d.setPMonth(0); i < m; d.setPMonth(++i)) {
            num += d.getPDaysInMonth();
        }
        return num + this.getPDate() - 1;
    }

    Date.prototype.getWeekOfYear = function() {
                var days=this.getPDayOfYear();
                return Math.ceil(days/7);
    }

    /**
     * Checks if the current date falls within a leap year in Persian date.
     * @return {Boolean} True if the current date falls within a leap year, false otherwise.
     */
    Date.prototype.isKabiseYear = function() {
        var year = this.getPFullYear();
        var mod=year%33;
        if(mod==1 || mod==5 || mod==9 || mod==13 || mod==17 || mod==22 || mod==26 || mod==30)return true;

        return false
    }

    /**
     * Get the first day of the current month, adjusted for leap year.  The returned value
     * is the numeric day index within the week (0-6) which can be used in conjunction with
     * the {@link #monthNames} array to retrieve the textual day name.
     * Example:
     * <pre><code>
var dt = new Date('1/10/2007');
document.write(Date.dayNames[dt.getFirstDayOfMonth()]); //output: 'Monday'
</code></pre>
     * @return {Number} The day number (0-6).
     */
    Date.prototype.getPFirstDayOfMonth = function() {
        
         var B= new Date();
         B.setPDate(1);
         B.setPMonth(this.getPMonth());
         B.setFullYear(this.getFullYear());
         return B.getPDay();
    }

    /**
     * Get the date of the last day of the month in which this date resides.
     * @return {Date}
     */
    Date.prototype.getPLastDateOfMonth = function() {
        g=Date.PersianToGregorian(this.getPFullYear(),this.getPMonth()+1,this.getPDaysInMonth())
        return new Date(g[0], g[1]-1, g[2]);
    }

    /**
     * Get the number of days in the current month, adjusted for leap year.
     * @return {Number} The number of days in the month.
     */
    Date.prototype.getPDaysInMonth = function() {
            var m = this.getPMonth();

            return m == 12 && this.isKabiseYear() ? 30 : Date.j_days_in_month[m];
       
    }
     
    Date.prototype.Padd = function(interval, value) {
        var d = this;
        if (!interval || value === 0) return d;

        switch(interval.toLowerCase()) {
            case Date.MILLI:
                d.setMilliseconds(this.getMilliseconds() + value);
                break;
            case Date.SECOND:
                d.setSeconds(this.getSeconds() + value);
                break;
            case Date.MINUTE:
                d.setMinutes(this.getMinutes() + value);
                break;
            case Date.HOUR:
                d.setHours(this.getHours() + value);
                break;
            case Date.DAY:
                d.setPDate(this.getPDate() + value);
                break;
            case Date.MONTH:
                d.setPMonth(this.getPMonth() + value);
                break;
            case Date.YEAR:
                d.setPFullYear(this.getPFullYear() + value);
                break;
        }
        return d;
    }

Date.prototype.getPFirstDateOfMonth = function() {
    var gd = this.getDate();
        var gm = this.getMonth();
        var gy = this.getFullYear();
        var j = Date.GregorianToPersian(gy, gm+1, gd);
        return new Date(j[0], j[1]-1, j[2]);
    }