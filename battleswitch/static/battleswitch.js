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
        ship_div = $('<button/>');
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
  var create_handler = function (i) {
    return function () {
      $.ajax({
        type: 'POST',
        url: '/toggle',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({'cell': i})
      });
    }
  };

  for (var i = 0; i < width*height; i++) {
    $('#preparing_board' + i).click(create_handler(i));
  }
}

function set_cell(board, cell_number, state) {
  console.assert(board === 'preparing_board' || board === 'own_board' || board === 'enemy_board');
  console.assert(cell_number >= 0 && cell_number < width*height);
  console.assert(state === 'empty' || state === 'present' || state === 'hit');
  var e = $('#' + board + cell_number);
  e.attr('class', 'ship ' + state);
  if (state === 'present') {
    e.text('🚢');
  } else if (state === 'hit') {
    e.text('💣');
  } else {
    e.text('');
  }
}

function set_board(board, cells) {
  for (var i = 0; i < width*height; i++) {
    set_cell(board, i, translate(cells[i]));
  }
}

function enable_element(element_id) {
  $('#' + element_id).css('display', '');
}

function disable_element(element_id) {
  $('#' + element_id).css('display', 'none');
}

function disable_all_elements() {
  disable_element('error');
  disable_element('preparing');
  disable_element('ready');
  disable_element('running');
  disable_element('over');
}

function request_state() {
  var on_success = function(data) {
    disable_all_elements();

    $('#player').text('You are player ' + (data.state.player + 1) + '.');

    switch (data.state.state) {
      case 'PREPARING':
        enable_element('preparing');
        set_board('preparing_board', data.state.own);
        $('#prepare_button').css('visibility', '');
        break;

      case 'READY':
        enable_element('preparing');
        set_board('preparing_board', data.state.own);
        $('#prepare_button').css('visibility', 'hidden');
        break;

      case 'RUNNING':
        enable_element('running');
        set_board('own_board', data.state.own);
        set_board('enemy_board', data.state.enemy);
        break;

      case 'WON':
        enable_element('over');
        $('#over_text').text('You won! 🏆');
        break;

      case 'LOST':
        enable_element('over');
        $('#over_text').text('You lost! 💀');
        break;

      default:
        enable_element('error');
        break;
    }

    setTimeout(request_state, 500);
  };

  var on_error = function () {
    disable_all_elements();
    enable_element('error');
  };

  $.ajax({
    url: '/state',
    dataType: 'json',
    success: on_success,
    error: on_error,
    timeout: 10000
  });
}

$(document).ready(function() {
  $('#prepare_button').click(function () {
    $.post('/ready');
  });

  $('#reset_button').click(function () {
    $.post('/reset');
  });

  $.getJSON('/config', function(data) {
    width = data.config.board.width;
    height = data.config.board.height;
    initialize_board();
    initialize_prepare_handlers();
    request_state();
  });

});

/* vim: set ts=8 sts=2 sw=2 et: */
