'use strict';

//var request = require('superagent');
var C = require('./constants');

/**
 * Automatic div module.
 * @module autodiv
 */

function parseMarkup(str) {
  var lines = str.split('\n'), data = [];

  // Handle div contents as diagram contents
  for(var i = 0, len = lines.length; i < len; ++i) {
    var elems = [], line = lines[i];

    for(var j = 0, len2 = line.length; j < len2; ++j) {
      switch(line[j]) {
        case '.':
          elems.push({type: C.CLEAR}); break;
        case 'o':
          elems.push({type: C.WHITE}); break;
        case 'x':
          elems.push({type: C.BLACK}); break;
        case ' ':
          break; // ignore whitespace
        default: // assume marker
          if(!elems.length) break; // no intersection yet
          // Append to mark so x123 etc. are possible
          if(elems[elems.length - 1].mark)
            elems[elems.length - 1].mark += line[j];
          else
            elems[elems.length - 1].mark = line[j];
      }
    }

    if(elems.length) data.push(elems);
  }

  return data;
}

// Array of loaded boards
//var boards = [];

// Available attributes:
// data-jgostyle: Evaluated and used as board style
// data-jgosize: Used as board size unless data-jgosgf is defined
// data-jgoview: Used to define viewport
function process(JGO, div) {
  // Handle special jgo-* attributes
  var style, width, height, TL, BR; // last two are viewport

  if(div.getAttribute('data-jgostyle')) {
    /*jshint evil:true  */
    style = eval(div.getAttribute('data-jgostyle'));
  } else style = JGO.BOARD.medium;

  if(div.getAttribute('data-jgosize')) {
    var size = div.getAttribute('data-jgosize');

    if(size.indexOf('x') != -1) {
      width = parseInt(size.substring(0, size.indexOf('x')));
      height = parseInt(size.substr(size.indexOf('x')+1));
    } else width = height = parseInt(size);
  }

  //if(div.getAttribute('data-jgosgf'))

  var data = parseMarkup(div.innerHTML);
  div.innerHTML = '';

  if(!width) { // Size still missing
    if(!data.length) return; // no size or data, no board

    height = data.length;
    width = data[0].length;
  }

  var jboard = new JGO.Board(width, height);
  var jsetup = new JGO.Setup(jboard, style);

  if(div.getAttribute('data-jgoview')) {
    var tup = div.getAttribute('data-jgoview').split('-');
    TL = jboard.getCoordinate(tup[0]);
    BR = jboard.getCoordinate(tup[1]);
  } else {
    TL = new JGO.Coordinate(0,0);
    BR = new JGO.Coordinate(width-1, height-1);
  }

  jsetup.view(TL.i, TL.j, width-TL.i, height-TL.j);

  var c = new JGO.Coordinate();

  for(c.j = TL.j; c.j <= BR.j; ++c.j) {
    for(c.i = TL.i; c.i <= BR.i; ++c.i) {
      var elem = data[c.j - TL.j][c.i - TL.i];
      jboard.setType(c, elem.type);
      if(elem.mark) jboard.setMark(c, elem.mark);
    }
  }

  jsetup.create(div);
}

/**
 * Find all div elements with class 'jgoboard' and initialize them.
 */
exports.init = function(document, JGO) {
  var matches = document.querySelectorAll('div.jgoboard');

  for(var i = 0, len = matches.length; i < len; ++i)
    process(JGO, matches[i]);
};
