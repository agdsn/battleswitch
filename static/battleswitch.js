var width = null;
var height = null;

function translate(state) {
  switch (state) {
    case 0: return 'empty';
    case 1: return 'present';
    case 2: return 'hit';
  }
  console.assert(false, 'Should not be reached.');
}

function initialize_board() {
  function helper(board) {
    var board_div = $('#' + board);
    var i = 0;
    for (var r = 0; r < height; r++) {
      var row_div = $('<div/>')
      row_div.attr('class', 'row');
      board_div.append(row_div);

      for (var c = 0; c < width; c++) {
        ship_div = $('<div/>');
        ship_div.attr('class', 'ship');
        ship_div.attr('id', board + i);
        row_div.append(ship_div);
        i++;
      }
    }
  }

  helper('preparing_board');
  helper('own_board');
  helper('enemy_board');
}

function initialize_prepare_handlers() {
  for (var i = 0; i < width*height; i++) {
    $('#preparing_board' + i).click(function () {
      $.post('toggle', {'port': i});
    });
  }
}

function set_port(board, port_number, state) {
  console.assert(board === 'preparing_board' || board === 'own_board' || board === 'enemy_board');
  console.assert(port_number >= 0 && port_number < width*height);
  console.assert(state === 'empty' || state === 'present' || state === 'hit');
  var e = $('#' + board + port_number);
  e.attr('class', 'ship ' + state);
  if (state === 'present') {
    e.text('🚢');
  } else if (state === 'hit') {
    e.text('💣');
  } else {
    e.text('');
  }
}

function request_state() {
  $.getJSON('state', function(data) {
    var preparing_display = 'none';
    var running_display = 'none';
    var over_display = 'none';
    if (data.state === 'preparing') {
      preparing_display = ''; 
      for (var i = 0; i < width*height; i++) {
        set_port('preparing_board', i, translate(data.own[i]));
      }
    } else if (data.state === 'running') {
      running_display = '';
      for (var i = 0; i < width*height; i++) {
        set_port('own_board', i, translate(data.own[i]));
        set_port('enemy_board', i, translate(data.enemy[i]));
      }
    } else if (data.state === 'over') {
      over_display = '';
    }

    $('#preparing').css('display', preparing_display);
    $('#running').css('display', running_display);
    $('#over').css('display', over_display);
  });

  setTimeout(request_state, 1000);
}

$(document).ready(function() {
  $('#prepare_button').click(function () {
    $.post('go');
  });

  $.getJSON('config', function(data) {
    width = data.board.width;
    height = data.board.height;
    initialize_board();
    initialize_prepare_handlers();
    request_state();
  });

});

/* vim: set ts=8 sts=2 sw=2 et: */
