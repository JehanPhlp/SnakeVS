const io = require('socket.io')(3000, {
    cors: {
      origin: "*",
    }
  });
  
  let waitingPlayer = null;
  let games = {};
  
  io.on('connection', socket => {
    console.log('Nouvelle connexion :', socket.id);
  
    // Recevoir l'ID du joueur
    socket.on('player_id', data => {
      socket.player_id = data.player_id;
      console.log(`Joueur connecté avec player_id: ${socket.player_id}`);
  
      if (waitingPlayer) {
        // Créer une nouvelle partie
        const gameRoom = `game-${waitingPlayer.id}-${socket.id}`;
        socket.join(gameRoom);
        waitingPlayer.join(gameRoom);
        socket.gameRoom = gameRoom;
        waitingPlayer.gameRoom = gameRoom;
  
        // Assigner des rôles aux joueurs
        const player1 = waitingPlayer;
        const player2 = socket;
        const game = {
          players: [player1, player2],
          lives: {
            [player1.id]: 3,
            [player2.id]: 3
          },
          roles: {
            [player1.id]: 'player1',
            [player2.id]: 'player2'
          },
          food: generateFoodPosition()
        };
        games[gameRoom] = game;
  
        // Envoyer le rôle à chaque joueur
        player1.emit('assign_role', { role: 'player1' });
        player1.emit('enemy_id', { enemy_id: player2.player_id });

        player2.emit('assign_role', { role: 'player2' });
        player2.emit('enemy_id', { enemy_id: player1.player_id });

        console.log(`Rôle 'player1' assigné à ${player1.id}`);
        console.log(`Rôle 'player2' assigné à ${player2.id}`);
        
        // Notifier les joueurs que la partie commence
        io.to(gameRoom).emit('game_start');
  
        // Démarrer la partie après 5 secondes
        setTimeout(() => {
          io.to(gameRoom).emit('start_game');
          // Envoyer la position initiale de la nourriture
          io.to(gameRoom).emit('update_food', { position: game.food });
        }, 5000);
  
        waitingPlayer = null;
      } else {
        // Mettre le joueur en attente
        waitingPlayer = socket;
        socket.emit('waiting', { message: 'En attente d\'un autre joueur...' });
      }
    });
  
    // Gérer la déconnexion en milieu de partie
    socket.on('disconnect', () => {
      console.log('Déconnexion :', socket.id);
      if (waitingPlayer && waitingPlayer.id === socket.id) {
          waitingPlayer = null;
      }
      // Gérer la déconnexion en milieu de partie
      const gameRoom = socket.gameRoom;
      if (gameRoom && games[gameRoom]) {
          const otherPlayerId = getOtherPlayerId(socket, gameRoom);
          const winnerPlayerId = getPlayerBySocketId(otherPlayerId).player_id;
          io.to(gameRoom).emit('game_over', { winner_id: winnerPlayerId });
          delete games[gameRoom];
      }
    });
      
    // Gestion des autres événements (update_position, eat_food, lose_life, etc.)
    socket.on('update_position', data => {
      const gameRoom = socket.gameRoom;
      if (gameRoom && games[gameRoom]) {
        // Envoyer la position du serpent à l'autre joueur
        socket.to(gameRoom).emit('update_other_snake', { body: data.body });
      }
    });
  
    // Gérer la consommation de la nourriture
    socket.on('eat_food', () => {
        const gameRoom = socket.gameRoom;
        if (gameRoom && games[gameRoom]) {
            // Générer une nouvelle position pour la nourriture
            games[gameRoom].food = generateFoodPosition();
            // Envoyer la nouvelle position aux deux joueurs
            io.to(gameRoom).emit('update_food', { position: games[gameRoom].food });
        }
    });
  
    // Gérer la perte de vie
    socket.on('lose_life', () => {
      const gameRoom = socket.gameRoom;
      if (gameRoom && games[gameRoom]) {
          games[gameRoom].lives[socket.id] -= 1;
          const otherPlayerId = getOtherPlayerId(socket, gameRoom);
          // Envoyer la mise à jour des vies
          socket.emit('update_lives', {
              your_lives: games[gameRoom].lives[socket.id],
              other_lives: games[gameRoom].lives[otherPlayerId]
          });
          io.to(otherPlayerId).emit('update_lives', {
              your_lives: games[gameRoom].lives[otherPlayerId],
              other_lives: games[gameRoom].lives[socket.id]
          });
          // Vérifier si le joueur a perdu toutes ses vies
          if (games[gameRoom].lives[socket.id] <= 0) {
              const winnerPlayerId = getPlayerBySocketId(otherPlayerId).player_id;
              io.to(gameRoom).emit('game_over', { winner_id: winnerPlayerId });
              delete games[gameRoom];
          }
      }
    });
  
    // Gérer la fin de la partie
    socket.on('game_over', () => {
      const gameRoom = Object.keys(socket.rooms).find(r => r.startsWith('game-'));
      if (gameRoom && games[gameRoom]) {
        io.to(gameRoom).emit('game_over', { winner: 'L\'autre joueur a gagné !' });
        delete games[gameRoom];
      }
    });
  });
  
  function generateFoodPosition() {
    return [Math.floor(Math.random() * 30), Math.floor(Math.random() * 20)];
  }
  
  function getOtherPlayerId(socket, gameRoom) {
    return games[gameRoom].players.find(player => player.id !== socket.id).id;
  }

  function getPlayerBySocketId(socketId) {
    for (let gameRoom in games) {
        const game = games[gameRoom];
        const player = game.players.find(player => player.id === socketId);
        if (player) {
            return player;
        }
    }
    return null;
  }
