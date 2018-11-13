'use strict';

/**
 * SGF loading module.
 * @module sgf
 */

var Coordinate = require('./coordinate');
var Record = require('./record');
var C = require('./constants');

var ERROR; // error holder for sgfParse etc.

var fieldMap = {
  'AN': 'annotator',
  'CP': 'copyright',
  'DT': 'date',
  'EV': 'event',
  'GN': 'gameName',
  'OT': 'overtime',
  'RO': 'round',
  'RE': 'result',
  'RU': 'rules',
  'SO': 'source',
  'TM': 'time',
  'PC': 'location',
  'PB': 'black',
  'PW': 'white',
  'BR': 'blackRank',
  'WR': 'whiteRank',
  'BT': 'blackTeam',
  'WT': 'whiteTeam'
};

/*
 * Helper function to handle single coordinates as well as coordinate lists.
 *
 * @param {object} propValues A property value array containing a mix of coordinates (aa) and lists (aa:bb)
 * @returns {array} An array of Coordinate objects matching the given property values.
 */
function explodeSGFList(propValues) {
  var coords = [];

  for(var i=0, len=propValues.length; i<len; i++) {
    var val = propValues[i];

    if(val.indexOf(':') == -1) { // single coordinate
      coords.push(new Coordinate(val));
    } else {
      var tuple = val.split(':'), c1, c2, coord;

      c1 = new Coordinate(tuple[0]);
      c2 = new Coordinate(tuple[1]);
      coord = new Coordinate();

      for(coord.i=c1.i; coord.i<=c2.i; ++coord.i)
        for(coord.j=c1.j; coord.j<=c2.j; ++coord.j)
          coords.push(coord.copy());
    }
  }

  return coords;
}

function sgfMove(node, name, values, moveMarks) {
  var coord, player, opponent, play;

  if(name == 'B') {
    player = C.BLACK;
    opponent = C.WHITE;
  } else if('W') {
    player = C.WHITE;
    opponent = C.BLACK;
  }

  coord = (values[0].length == 2) ? new Coordinate(values[0]) : null;

  // Apparently, IGS wants to use outside-board coordinates for pass
  if(coord !== null && (coord.i >= node.jboard.width || coord.j >= node.jboard.height))
    coord = null; // Thank you, IGS

  play = node.jboard.playMove(coord, player);
  node.info.captures[player] += play.captures.length; // tally captures

  if(moveMarks && play.ko)
      node.setMark(play.ko, C.MARK.SQUARE);
  
  if(play.success && coord !== null) {
    node.setType(coord, player); // play stone
    node.setType(play.captures, C.CLEAR); // clear opponent's stones
    if(moveMarks)
      node.setMark(coord, C.MARK.CIRCLE);
  } else ERROR = play.error;

  return play.success;
}

function sgfSetup(node, name, values) {
  var setupMap = {'AB': C.BLACK, 'AW': C.WHITE, 'AE': C.CLEAR};

  node.setType(explodeSGFList(values), setupMap[name]);
  return true;
}

function sgfMarker(node, name, values) {
  var markerMap = {
    'TW': C.MARK.WHITE_TERRITORY,
    'TB': C.MARK.BLACK_TERRITORY,
    'CR': C.MARK.CIRCLE,
    'TR': C.MARK.TRIANGLE,
    'MA': C.MARK.CROSS,
    'SQ': C.MARK.SQUARE
  };

  node.setMark(explodeSGFList(values), markerMap[name]);
  return true;
}

function sgfComment(node, name, values) {
  node.info.comment = values[0];
  return true;
}

function sgfHandicap(node, name, values) {
  node.info.handicap = values[0];
  return true;
}

function sgfLabel(node, name, values) {
  for(var i=0; i<values.length; i++) {
    var v = values[i], tuple = v.split(':');

    node.setMark(new Coordinate(tuple[0]), tuple[1]);
  }
  return true;
}

function sgfInfo(node, name, values) {
  var field = fieldMap[name];

  node.info[field] = values[0];
  return true;
}

var SGFProperties = {
  'B': sgfMove,
  'W': sgfMove,
  'AB': sgfSetup,
  'AW': sgfSetup,
  'AE': sgfSetup,
  'C': sgfComment,
  'LB': sgfLabel,
  'HA': sgfHandicap,
  'TW': sgfMarker,
  'TB': sgfMarker,
  'CR': sgfMarker,
  'TR': sgfMarker,
  'MA': sgfMarker,
  'SQ': sgfMarker,
  'AN': sgfInfo,
  'CP': sgfInfo,
  'DT': sgfInfo,
  'EV': sgfInfo,
  'GN': sgfInfo,
  'OT': sgfInfo,
  'RO': sgfInfo,
  'RE': sgfInfo,
  'RU': sgfInfo,
  'SO': sgfInfo,
  'TM': sgfInfo,
  'PC': sgfInfo,
  'PB': sgfInfo,
  'PW': sgfInfo,
  'BR': sgfInfo,
  'WR': sgfInfo,
  'BT': sgfInfo,
  'WT': sgfInfo
};

/*
 * Parse SGF string into object tree representation:
 *
 * tree = { sequence: [ <node(s)> ], leaves: [ <subtree(s), if any> ] }
 *
 * Each node is an object containing property identifiers and associated values in array:
 *
 * node = {'B': ['nn'], 'C': ['This is a comment']}
 *
 * @param {String} sgf The SGF in string format, whitespace allowed.
 * @returns {Object} Root node or false on error. Error stored to ERROR variable.
 */
function parseSGF(sgf) {
  var tokens, i, len, token, // for loop vars
      lastBackslash = false, // flag to note if last string ended in escape
      bracketOpen = -1, // the index where bracket opened
      processed = [];

  if('a~b'.split(/(~)/).length === 3) {
    tokens = sgf.split(/([\[\]\(\);])/); // split into an array at '[', ']', '(', ')', and ';', and include separators in array
  } else { // Thank you IE for not working
    var blockStart = 0, delimiters = '[]();';

    tokens = [];

    for(i=0, len=sgf.length; i<len; ++i) {
      if(delimiters.indexOf(sgf.charAt(i)) !== -1) {
        if(blockStart < i)
          tokens.push(sgf.substring(blockStart, i));
        tokens.push(sgf.charAt(i));
        blockStart = i+1;
      }
    }

    if(blockStart < i) // leftovers
      tokens.push(sgf.substr(blockStart, i));
  }

  // process through tokens and push everything into processed, but merge stuff between square brackets into one element, unescaping escaped brackets
  // i.e. ['(', ';', 'C', '[', 'this is a comment containing brackets ', '[', '\\', ']', ']'] becomes:
  // ['(', ';', 'C', '[', 'this is a comment containing brackets []]']
  // after this transformation, it's just '(', ')', ';', 'ID', and '[bracket stuff]' elements in the processed array
  for(i=0, len=tokens.length; i<len; ++i) {
    token = tokens[i];

    if(bracketOpen == -1) { // handling elements outside property values (i.e. square brackets)
      token = token.replace(/^\s+|\s+$/g, ''); // trim whitespace, it is irrelevant here
      if(token == '[') // found one
        bracketOpen = i;
      else if(token !== '') // we are outside brackets, so just push everything nonempty as it is into 'processed'
        processed.push(token);
    } else { // bracket is open, we're now looking for a ] without preceding \
      if(token != ']') { // a text segment
        lastBackslash = (token.charAt(token.length-1) == '\\'); // true if string ends in \
      } else { // a closing bracket
        if(lastBackslash) { // it's escaped - we continue
          lastBackslash = false;
        } else { // it's not escaped - we close the segment
          processed.push(tokens.slice(bracketOpen, i+1).join('').replace(/\\\]/g, ']')); // push the whole thing including brackets, and unescape the inside closing brackets
          bracketOpen = -1;
        }
      }
    }
  }

  // basic error checking
  if(processed.length === 0) {
    ERROR = 'SGF was empty!';
    return false;
  } else if(processed[0] != '(' || processed[1] != ';' || processed[processed.length-1] != ')') {
    ERROR = 'SGF did not start with \'(;\' or end with \')\'!';
    return false;
  }

  // collect 'XY', '[AB]', '[CD]' sequences (properties) in a node into {'XY': ['AB', 'CD']} type of associative array
  // effectively parsing '(;GM[1]FF[4];B[pd])' into ['(', {'GM': ['1'], 'FF': ['4']}, {'B': ['pd']}, ')']

  // start again with 'tokens' and process into 'processed'
  tokens = processed;
  processed = [];

  var node, propertyId = ''; // node under construction, and current property identifier

  // the following code is not strict on format, so let's hope it's well formed
  for(i=0, len=tokens.length; i<len; ++i) {
    token = tokens[i];

    if(token == '(' || token == ')') {
      if(node) { // flush and reset node if necessary
        if(propertyId !== '' && node[propertyId].length === 0) { // last property was missing value
          ERROR = 'Missing property value at ' + token + '!';
          return false;
        }
        processed.push(node);
        node = undefined;
      }

      processed.push(token); // push this token also
    } else if(token == ';') { // new node
      if(node) { // flush if necessary
        if(propertyId !== '' && node[propertyId].length === 0) { // last property was missing value
          ERROR = 'Missing property value at ' + token + '!';
          return false;
        }
        processed.push(node);
      }

      node = {};
      propertyId = ''; // initialize the new node
    } else { // it's either a property identifier or a property value
      if(token.indexOf('[') !== 0) { // it's property identifier
        if(propertyId !== '' && node[propertyId].length === 0) { // last property was missing value
          ERROR = 'Missing property value at ' + token + '!';
          return false;
        }

        if(token in node) { // duplicate key
          ERROR = 'Duplicate property identifier ' + token + '!';
          return false;
        }

        propertyId = token;
        node[propertyId] = []; // initialize new property with empty value array
      } else { // it's property value
        if(propertyId === '') { // we're missing the identifier
          ERROR = 'Missing property identifier at ' + token + '!';
          return false;
        }

        node[propertyId].push(token.substring(1, token.length-1)); // remove enclosing brackets
      }
    }
  }

  tokens = processed;

  // finally, construct a game tree from '(', ')', and sequence arrays - each leaf is {sequence: [ <list of nodes> ], leaves: [ <list of leaves> ]}
  var stack = [], currentRoot = {sequence: [], leaves: []}, lastRoot; // we know first element already: '('

  for(i=1, len=tokens.length; i<len-1; ++i) {
    token = tokens[i];

    if(token == '(') { // enter a subleaf
      if(currentRoot.sequence.length === 0) { // consecutive parenthesis without node sequence in between will throw an error
        ERROR = 'SGF contains a game tree without a sequence!';
        return false;
      }
      stack.push(currentRoot); // save current leaf for when we return
      currentRoot = {sequence: [], leaves: []};
    } else if(token == ')') { // return from subleaf
      if(currentRoot.sequence.length === 0) { // consecutive parenthesis without node sequence in between will throw an error
        ERROR = 'SGF contains a game tree without a sequence!';
        return false;
      }
      lastRoot = currentRoot;
      currentRoot = stack.pop();
      currentRoot.leaves.push(lastRoot);
    } else { // if every '(' is not followed by exactly one array of nodes (as it should), this code fails
      currentRoot.sequence.push(token);
    }
  }

  if(stack.length > 0) {
    ERROR = 'Invalid number of parentheses in the SGF!';
    return false;
  }

  return currentRoot;
}

/*
 * Apply SGF nodes recursively to create a game tree.
 * @returns true on success, false on error. Error message in ERROR.
 */
function recurseRecord(jrecord, gameTree, moveMarks) {
  for(var i=0; i<gameTree.sequence.length; i++) {
    var node = gameTree.sequence[i],
      jnode = jrecord.createNode(true); // clear parent marks

    for(var key in node) {
      if(node.hasOwnProperty(key)) {
        if(!(key in SGFProperties))
          continue;

        if(!SGFProperties[key](jnode, key, node[key], moveMarks)) {
          ERROR = 'Error while parsing node ' + key + ': ' + ERROR;
          return false;
        }
      }
    }
  }

  for(i=0; i<gameTree.leaves.length; i++) {
    var subTree = gameTree.leaves[i], snapshot;

    snapshot = jrecord.createSnapshot();

    if(!recurseRecord(jrecord, subTree, moveMarks))
      return false; // fall through on errors

    jrecord.restoreSnapshot(snapshot);
  }

  return true;
}

/*
 * Convert game tree to a record.
 * @returns {Object} Record or false on failure. Error stored in ERROR.
 */
function gameTreeToRecord(gameTree, moveMarks) {
  var jrecord, root = gameTree.sequence[0], width = 19, height = 19;

  if('SZ' in root) {
    var size = root.SZ[0];

    if(size.indexOf(':') != -1) {
      width = parseInt(size.substring(0, size.indexOf(':')));
      height = parseInt(size.substr(size.indexOf(':')+1));
    } else width = height = parseInt(size);
  }

  jrecord = new Record(width, height);

  if(!recurseRecord(jrecord, gameTree, moveMarks))
    return false;

  jrecord.first(); // rewind to start

  return jrecord;
}

/**
 * Parse SGF and return {@link Record} object(s).
 *
 * @param {String} sgf The SGF file as a string.
 * @param {bool} moveMarks Create move and ko marks in the record.
 * @returns {Object} Record object, array of them, or string on error.
 */
exports.load = function(sgf, moveMarks) {
  var gameTree = parseSGF(sgf);

  if(gameTree === false)
    return ERROR;

  if(gameTree.sequence.length === 0) { // potentially multiple records
    var ret = [];

    if(gameTree.leaves.length === 0)
      return 'Empty game tree!';

    for(var i=0; i<gameTree.leaves.length; i++) {
      var rec = gameTreeToRecord(gameTree, moveMarks);

      if(!rec)
        return ERROR;

      ret.push(rec); // return each leaf as separate record
    }

    return ret;
  }

  return gameTreeToRecord(gameTree, moveMarks);
};
