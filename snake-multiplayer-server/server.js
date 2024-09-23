const WebSocket = require("ws");
const wss = new WebSocket.Server({ port: 8080 });

let players = {}; // Contient les informations des joueurs et leur état de jeu (positions, vies, etc.)
let foodPosition = {
  x: Math.floor(Math.random() * 30),
  y: Math.floor(Math.random() * 20),
}; // Position aléatoire de la nourriture

// Fonction pour générer une nouvelle position pour la nourriture
function generateFood() {
  return {
    x: Math.floor(Math.random() * 30),
    y: Math.floor(Math.random() * 20),
  };
}

// Mise à jour des positions des serpents
function updatePositions() {
  for (let playerId in players) {
    let player = players[playerId];
    // Calcul de la nouvelle position en fonction de la direction
    switch (player.direction) {
      case "UP":
        player.position.y -= 1;
        break;
      case "DOWN":
        player.position.y += 1;
        break;
      case "LEFT":
        player.position.x -= 1;
        break;
      case "RIGHT":
        player.position.x += 1;
        break;
    }

    // Gérer les collisions avec la nourriture
    if (
      player.position.x === foodPosition.x &&
      player.position.y === foodPosition.y
    ) {
      player.score += 1; // Augmenter le score
      foodPosition = generateFood(); // Générer une nouvelle nourriture
    }
  }
}

// Diffuser l'état du jeu à tous les joueurs
function broadcastGameState() {
  const gameState = {
    players: players,
    food: foodPosition,
  };

  // Envoyer l'état du jeu à chaque joueur
  for (let playerId in players) {
    let ws = players[playerId].ws;
    ws.send(JSON.stringify({ type: "gameState", gameState: gameState }));
  }
}

// Lorsqu'un joueur se connecte
wss.on("connection", function connection(ws) {
  console.log("Un nouveau joueur est connecté.");

  const playerId = Date.now(); // ID unique pour le joueur
  players[playerId] = {
    id: playerId,
    lives: 3,
    position: {
      x: Math.floor(Math.random() * 30),
      y: Math.floor(Math.random() * 20),
    }, // Position initiale
    direction: "RIGHT", // Direction par défaut
    score: 0,
    ws: ws, // Stocker le WebSocket pour chaque joueur
  };

  // Envoyer l'ID et la position initiale au joueur
  ws.send(
    JSON.stringify({
      type: "welcome",
      id: playerId,
      position: players[playerId].position,
    })
  );

  // Gérer les messages reçus des joueurs
  ws.on("message", function incoming(message) {
    const data = JSON.parse(message);
    if (data.type === "move") {
      // Mettre à jour la direction du joueur
      players[playerId].direction = data.direction;
    }
  });

  // Gérer la déconnexion du joueur
  ws.on("close", function () {
    console.log(`Le joueur ${playerId} s'est déconnecté.`);
    delete players[playerId]; // Supprimer le joueur de la liste
  });
});

// Boucle de jeu principale
setInterval(function () {
  updatePositions(); // Mettre à jour les positions des serpents
  broadcastGameState(); // Envoyer l'état du jeu à tous les joueurs
}, 100); // 10 fois par seconde

function checkCollisions() {
  for (let playerId in players) {
    let player = players[playerId];

    // Vérifier les limites du terrain (30x20)
    if (
      player.position.x < 0 ||
      player.position.x >= 30 ||
      player.position.y < 0 ||
      player.position.y >= 20
    ) {
      player.lives -= 1;
      console.log(
        `Le joueur ${playerId} a perdu une vie. Vies restantes : ${player.lives}`
      );

      // Si le joueur a perdu toutes ses vies, il est éliminé
      if (player.lives <= 0) {
        delete players[playerId];
        console.log(`Le joueur ${playerId} est éliminé.`);
        broadcastGameState(); // Mettre à jour les autres joueurs
      }
    }

    // Vérifier la collision avec les autres joueurs
    for (let otherId in players) {
      if (
        playerId !== otherId &&
        players[otherId].position.x === player.position.x &&
        players[otherId].position.y === player.position.y
      ) {
        player.lives -= 1;
        console.log(
          `Le joueur ${playerId} est entré en collision avec un autre joueur.`
        );

        if (player.lives <= 0) {
          delete players[playerId];
          console.log(`Le joueur ${playerId} est éliminé après une collision.`);
          broadcastGameState();
        }
      }
    }
  }
}

// Boucle de jeu principale
setInterval(function () {
  updatePositions(); // Mettre à jour les positions des serpents
  checkCollisions(); // Vérifier les collisions et les vies
  broadcastGameState(); // Envoyer l'état du jeu à tous les joueurs
}, 100); // 10 fois par seconde

console.log("Serveur WebSocket démarré sur le port 8080");
