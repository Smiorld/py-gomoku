
var socket = io('/gomoku');
var sid;
var role;
var color;
var room_dict={};
function update_board(room) {
    // update the board
    host_set = JSON.parse(room['host_set']);
    guest_set = JSON.parse(room['guest_set']);
    for (let i = 0; i < host_set.length; i++) {
        let row = host_set[i][0];
        let col = host_set[i][1];
        let cell = document.getElementById(row + "-" + col);
        if (room['black']){
            cell.innerHTML=change_cell_to_color(row,col,'white');
        }else{
            cell.innerHTML=change_cell_to_color(row,col,'black');
        }
        cell.setAttribute("state", 1);
    }
    for (let i = 0; i < guest_set.length; i++) {
        let row = guest_set[i][0];
        let col = guest_set[i][1];
        let cell = document.getElementById(row + "-" + col);
        if (room['black']){
            cell.innerHTML=change_cell_to_color(row,col,'black');
        }else{
            cell.innerHTML=change_cell_to_color(row,col,'white');
        }
        cell.setAttribute("state", 2);
    }
}

function update_room_info(room) {
    // update the room info
    let output_panel = document.getElementById("j-right");
    output_panel.innerHTML = "<p id='room_id'>room id: "+room['id']+"</p>\n"+
    "<p id='room_name'>room name: "+room['name']+"</p>\n"+
    "<p id='room_host'>room host: "+room['host']+"</p>\n"+
    "<p id='room_guest'>room guest: "+room['guest']+"</p>\n"+
    "<p id='room_black'>room black: "+room['black']+"</p>\n"+
    "<p id='board_size'>board size: "+room['board_size']+"</p>\n"+
    "<p id='each_drop_time'>each drop time: "+room['each_drop_time']+"</p>\n"+
    "<p id='gaming_status'>gaming status: "+room['gaming_status']+"</p>\n"+
    "<p id='turn'>turn: "+room['turn']+"</p>\n"+
    "<p id='host_set'>host set: "+room['host_set']+"</p>\n"+
    "<p id='guest_set'>guest set: "+room['guest_set']+"</p>\n"+
    "<p id='gold_finger_set'>gold finger set: "+room['gold_finger_set']+"</p>\n"+
    "<p id='watcher_number'>watcher number: "+room['watcher_number']+"</p>\n"+
    "<p id='watcher_list'>watcher list: "+room['watcher_list']+"</p>\n"+
    "----------------------------------------\n"+
    "<p id='client_role'>your sid is: "+sid+"</p>\n";
    if (room['host']==sid){
        output_panel.innerHTML += "<p id='client_role'>your role is: host</p>\n";
        role='host';
        if (room['black']){
            output_panel.innerHTML += "<p id='client_role'>your color is: white</p>\n";
            color='white';
        }else{
            output_panel.innerHTML += "<p id='client_role'>your color is: black</p>\n";
            color='black';
        }
    }else if (room['guest']==sid){
        output_panel.innerHTML += "<p id='client_role'>your role is: guest</p>\n";
        role='guest';
        if (room['black']){
            output_panel.innerHTML += "<p id='client_role'>your color is: black</p>\n";
            color='black';
        }else{
            output_panel.innerHTML += "<p id='client_role'>your color is: white</p>\n";
            color='white';
        }
    }else{
        output_panel.innerHTML += "<p id='client_role'>your role is: watcher</p>\n";
        role='watcher';
    }
    if (role=='host' && !room['gaming_status'] && room['guest']!=null){
        output_panel.innerHTML += '<button onclick=start_game() class="w3-button w3-blue" style="border-radius:5px" value="Start game">Start game</button>\n';
    }

    
}

function start_game(){
    if (role=='host' && !room_dict['gaming_status'] && room_dict['guest']!=null){
        let room_id = room_dict['id'];
        socket.emit('start game', {'room_id':room_id});
    }
    else{
        alert('You are not the host or the game has already started!');
    }
}

function change_cell_to_color(row,col,color){
    if (color=='white'){
        if (row==0){
            if (col==0){
                img = "<img src='/static/img/left_top_white.png'>";
            }else if (col==room_dict['board_size']-1){
                img = "<img src='/static/img/right_top_white.png'>";
            }else{
                img = "<img src='/static/img/top_white.png'>";
            }
        }else if (row==room_dict['board_size']-1){
            if (col==0){
                img = "<img src='/static/img/left_bot_white.png'>";
            }else if (col==room_dict['board_size']-1){
                img = "<img src='/static/img/right_bot_white.png'>";
            }else{
                img = "<img src='/static/img/bot_white.png'>";
            }
        }else{
            if (col==0){
                img = "<img src='/static/img/left_white.png'>";
            }else if (col==room_dict['board_size']-1){
                img = "<img src='/static/img/right_white.png'>";
            }else{
                img = "<img src='/static/img/center_white.png'>";
            }
        }
    }else if (color=='black'){
        if (row==0){
            if (col==0){
                img = "<img src='/static/img/left_top_black.png'>";
            }else if (col==room_dict['board_size']-1){
                img = "<img src='/static/img/right_top_black.png'>";
            }else{
                img = "<img src='/static/img/top_black.png'>";
            }
        }else if (row==room_dict['board_size']-1){
            if (col==0){
                img = "<img src='/static/img/left_bot_black.png'>";
            }else if (col==room_dict['board_size']-1){
                img = "<img src='/static/img/right_bot_black.png'>";
            }else{
                img = "<img src='/static/img/bot_black.png'>";
            }
        }else{
            if (col==0){
                img = "<img src='/static/img/left_black.png'>";
            }else if (col==room_dict['board_size']-1){
                img = "<img src='/static/img/right_black.png'>";
            }else{
                img = "<img src='/static/img/center_black.png'>";
            }
        }
    }

    
    return img;
}

function place_a_piece(i,j) {
    // attempt to drop a piece on the board
    if ( room_dict['gaming_status'] && (role=='host' || role=='guest') ){
        // check if it is this player's turn
        console.log(role,room_dict['turn']);
        console.log(role=='guest')==(room_dict['turn']);
        if ( (role=='guest')==(room_dict['turn']) ){
            // player's turn
            let cell=document.getElementById(i+'-'+j);
            let state=cell.getAttribute('state');
            if (state==0){
                // place a piece
                socket.emit('place a piece', { 'room_id':1,'row':i,'col':j,'role':role,'board_size':room_dict['board_size'] });
            }
    }else{
        // player is watcher or game not started, do nothing.
    }

    };
}

socket.on('message', function(msg) {
    // when receive a message from the server, display it on the screen
    alert(msg);
});

socket.on('connect', function() {
    // if successfully connect to the server, attempt to join the room
    // account system not implemented yet, so a player is allowed to join multiple rooms for multiple times.
    socket.emit('join', {'room_id':1});
    sid= socket.id;
});

socket.on('update room', function(room) {
    // update the room information
    room_dict=room;
    update_board(room);
    update_room_info(room);
});

socket.on('room reject', function(data){
    // reject by the room for some reason
    alert(房间已满或您已经在房间中);
    window.location.replace("http://www.w3schools.com");
});

