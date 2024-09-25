const io = require("socket.io")(3000, {
  cors: {
    origin: "*",
  },
});

let waitingPlayer = null;
let games = {};

io.on("connection", (socket) => {
  console.log("Nouvelle connexion :", socket.id);

  // Recevoir l'ID du joueur
  socket.on("player_id", (data) => {
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
        gameRoom: gameRoom,
        players: [player1, player2],
        lives: {
          [player1.id]: 3,
          [player2.id]: 3,
        },
        roles: {
          [player1.id]: "player1",
          [player2.id]: "player2",
        },
        snakes: {},
        interval: null, // Pour stocker l'intervalle de la boucle de jeu
      };

      // Définir le jeu dans la liste des jeux actifs
      games[gameRoom] = game;

      // Envoyer le rôle à chaque joueur
      player1.emit("assign_role", { role: "player1" });
      player1.emit("enemy_id", { enemy_id: player2.player_id });

      player2.emit("assign_role", { role: "player2" });
      player2.emit("enemy_id", { enemy_id: player1.player_id });

      console.log(`Rôle 'player1' assigné à ${player1.id}`);
      console.log(`Rôle 'player2' assigné à ${player2.id}`);

      // Notifier les joueurs que la partie commence
      io.to(gameRoom).emit("game_start");

      // Démarrer la partie après 5 secondes
      setTimeout(() => {
        io.to(gameRoom).emit("start_game");
        startGame(gameRoom); // Démarrer le jeu ici
      }, 5000);

      waitingPlayer = null;
    } else {
      // Mettre le joueur en attente
      waitingPlayer = socket;
      socket.emit("waiting", { message: "En attente d'un autre joueur..." });
    }
  });

  // Gérer la déconnexion en milieu de partie
  socket.on("disconnect", () => {
    console.log("Déconnexion :", socket.id);
    if (waitingPlayer && waitingPlayer.id === socket.id) {
      waitingPlayer = null;
    }
    // Gérer la déconnexion en milieu de partie
    const gameRoom = socket.gameRoom;
    if (gameRoom && games[gameRoom]) {
      const otherPlayerId = getOtherPlayerId(socket, gameRoom);
      const winnerPlayerId = getPlayerBySocketId(otherPlayerId).player_id;
      io.to(gameRoom).emit("game_over", { winner_id: winnerPlayerId });
      clearInterval(games[gameRoom].interval); // Arrêter la boucle de jeu
      delete games[gameRoom];
    }
  });

  // Gestion des autres événements
  socket.on("change_direction", (data) => {
    const gameRoom = socket.gameRoom;
    if (gameRoom && games[gameRoom]) {
      const game = games[gameRoom];
      const direction = getDirectionVector(data.direction);
      if (!isOppositeDirection(game.snakes[socket.id].direction, direction)) {
        game.snakes[socket.id].nextDirection = direction;
      }
    }
  });
});

function startGame(gameRoom) {
  const game = games[gameRoom];
  // Initialiser les serpents
  game.snakes = {
    [game.players[0].id]: {
      body: initializeSnakeBody("player1"),
      direction: [1, 0], // Direction initiale pour le joueur 1
      nextDirection: [1, 0],
    },
    [game.players[1].id]: {
      body: initializeSnakeBody("player2"),
      direction: [-1, 0], // Direction initiale pour le joueur 2
      nextDirection: [-1, 0],
    },
  };
  // Maintenant que les serpents sont initialisés, générer la nourriture
  game.food = generateFoodPosition(game);
  // Envoyer la position initiale de la nourriture aux joueurs
  io.to(gameRoom).emit("update_food", { position: game.food });
  // Démarrer la boucle de jeu
  game.interval = setInterval(() => {
    updateGameState(gameRoom);
  }, 200); // Mettre à jour toutes les 200 ms
}

function updateGameState(gameRoom) {
  const game = games[gameRoom];
  if (!game) return;

  // Déplacer les serpents
  game.players.forEach((player) => {
    moveSnake(game, player.id);
  });

  // Vérifier les collisions et mettre à jour les vies
  checkCollisions(game);

  // Envoyer l'état du jeu aux clients
  game.players.forEach((player) => {
    const otherPlayerId = getOtherPlayerId(player, gameRoom);
    player.emit("game_state", {
      your_snake: game.snakes[player.id].body,
      other_snake: game.snakes[otherPlayerId].body,
      food: game.food,
      your_lives: game.lives[player.id],
      other_lives: game.lives[otherPlayerId],
    });
  });
}

function moveSnake(game, playerId) {
  const snake = game.snakes[playerId];
  // Mettre à jour la direction
  snake.direction = snake.nextDirection;
  const direction = snake.direction;
  const newHead = [
    snake.body[0][0] + direction[0],
    snake.body[0][1] + direction[1],
  ];
  snake.body.unshift(newHead);
  // Vérifier si le serpent a mangé la nourriture
  if (newHead[0] === game.food[0] && newHead[1] === game.food[1]) {
    // Générer une nouvelle nourriture
    game.food = generateFoodPosition(game); // Assurez-vous de passer 'game' ici
  } else {
    // Enlever la queue
    snake.body.pop();
  }
}

function checkCollisions(game) {
  game.players.forEach((player) => {
    const playerId = player.id;
    const snake = game.snakes[playerId];
    const head = snake.body[0];

    let collisionOccurred = false;

    // Collision avec les murs
    if (head[0] < 0 || head[0] >= 30 || head[1] < 0 || head[1] >= 20) {
      game.lives[playerId] -= 1;
      collisionOccurred = true;
    }

    // Collision avec soi-même
    for (let i = 1; i < snake.body.length; i++) {
      if (head[0] === snake.body[i][0] && head[1] === snake.body[i][1]) {
        game.lives[playerId] -= 1;
        collisionOccurred = true;
        break;
      }
    }

    // Collision avec l'autre serpent
    const otherPlayerId = getOtherPlayerId(player, game.gameRoom);
    const otherSnake = game.snakes[otherPlayerId];
    for (let part of otherSnake.body) {
      if (head[0] === part[0] && head[1] === part[1]) {
        game.lives[playerId] -= 1;
        collisionOccurred = true;
        break;
      }
    }

    if (collisionOccurred) {
      if (game.lives[playerId] <= 0) {
        endGame(game, otherPlayerId);
      } else {
        resetSnake(game, playerId);
      }
    }
  });
}

function resetSnake(game, playerId) {
  const role = game.roles[playerId];
  game.snakes[playerId] = {
    body: initializeSnakeBody(role),
    direction: role === "player1" ? [1, 0] : [-1, 0],
    nextDirection: role === "player1" ? [1, 0] : [-1, 0],
  };
}

function endGame(game, winnerId) {
  // Arrêter la boucle de jeu
  clearInterval(game.interval);
  // Envoyer l'événement de fin de jeu aux joueurs
  game.players.forEach((player) => {
    player.emit("game_over", { winner_id: winnerId });
  });
  // Supprimer le jeu de la liste des jeux actifs
  delete games[game.gameRoom];
}

function getDirectionVector(directionString) {
  switch (directionString) {
    case "UP":
      return [0, -1];
    case "DOWN":
      return [0, 1];
    case "LEFT":
      return [-1, 0];
    case "RIGHT":
      return [1, 0];
    default:
      return [0, 0];
  }
}

function isOppositeDirection(dir1, dir2) {
  return dir1[0] === -dir2[0] && dir1[1] === -dir2[1];
}

function initializeSnakeBody(role) {
  if (role === "player1") {
    return [
      [2, 18],
      [1, 18],
      [0, 18],
    ];
  } else if (role === "player2") {
    return [
      [27, 1],
      [28, 1],
      [29, 1],
    ];
  }
}

function generateFoodPosition(game) {
  let position;
  let valid;
  do {
    position = [Math.floor(Math.random() * 30), Math.floor(Math.random() * 20)];
    valid = true;
    // Vérifier que la nourriture n'apparaît pas sur un serpent
    game.players.forEach((player) => {
      const snake = game.snakes[player.id];
      for (let part of snake.body) {
        if (part[0] === position[0] && part[1] === position[1]) {
          valid = false;
          break;
        }
      }
    });
  } while (!valid);
  return position;
}

function getOtherPlayerId(socketOrPlayer, gameRoom) {
  const game = games[gameRoom];
  return game.players.find((player) => player.id !== socketOrPlayer.id).id;
}

function getPlayerBySocketId(socketId) {
  for (let gameRoom in games) {
    const game = games[gameRoom];
    const player = game.players.find((player) => player.id === socketId);
    if (player) {
      return player;
    }
  }
  return null;
}
