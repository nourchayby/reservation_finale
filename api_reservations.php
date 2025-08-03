<?php
header("Content-Type: application/json");
$mysqli = new mysqli("localhost", "root", "", "reservation_salle");

if ($mysqli->connect_errno) {
    echo json_encode(["status" => "error", "message" => "Erreur connexion BDD"]);
    exit();
}

$data = json_decode(file_get_contents("php://input"), true);
$action = $data["action"];

if ($action === "add") {
    $nom = $data["nom"];
    $email = $data["email"];
    $telephone = $data["telephone"];
    $objet = $data["objet"];
    $date = $data["date_reservation"];
    $heure_debut = $data["heure_debut"];
    $heure_fin = $data["heure_fin"];

    // Vérifier si l'utilisateur existe déjà
    $stmt = $mysqli->prepare("SELECT id FROM users WHERE email = ?");
    $stmt->bind_param("s", $email);
    $stmt->execute();
    $stmt->bind_result($id_user);
    $stmt->fetch();
    $stmt->close();

    if (!$id_user) {
        // Ajouter un nouvel utilisateur
        $stmt_insert = $mysqli->prepare("INSERT INTO users (nom, email, telephone) VALUES (?, ?, ?)");
        $stmt_insert->bind_param("sss", $nom, $email, $telephone);
        $stmt_insert->execute();
        $id_user = $stmt_insert->insert_id;
        $stmt_insert->close();
    }

    // Insérer la réservation
    $stmt_res = $mysqli->prepare("INSERT INTO reservations (id_user, date_reservation, heure_debut, heure_fin, objet) VALUES (?, ?, ?, ?, ?)");
    $stmt_res->bind_param("issss", $id_user, $date, $heure_debut, $heure_fin, $objet);

    if ($stmt_res->execute()) {
        echo json_encode(["status" => "success", "message" => "Réservation ajoutée avec succès"]);
    } else {
        echo json_encode(["status" => "error", "message" => "Erreur lors de l'ajout"]);
    }
    $stmt_res->close();
} elseif ($action === "delete") {
    $email = $data["email"];
    $date = $data["date_reservation"];
    $heure_debut = $data["heure_debut"];
    $heure_fin = $data["heure_fin"];

    $stmt_user = $mysqli->prepare("SELECT id FROM users WHERE email = ?");
    $stmt_user->bind_param("s", $email);
    $stmt_user->execute();
    $stmt_user->bind_result($id_user);
    $stmt_user->fetch();
    $stmt_user->close();

    if ($id_user) {
        $stmt_del = $mysqli->prepare("DELETE FROM reservations WHERE id_user = ? AND date_reservation = ? AND heure_debut = ? AND heure_fin = ?");
        $stmt_del->bind_param("isss", $id_user, $date, $heure_debut, $heure_fin);
        if ($stmt_del->execute()) {
            echo json_encode(["status" => "success", "message" => "Réservation supprimée avec succès"]);
        } else {
            echo json_encode(["status" => "error", "message" => "Erreur suppression"]);
        }
        $stmt_del->close();
    } else {
        echo json_encode(["status" => "error", "message" => "Utilisateur non trouvé"]);
    }
} elseif ($action === "edit") {
    $nom = $data["nom"];
    $email = $data["email"];
    $telephone = $data["telephone"];
    $objet = $data["objet"];
    $date = $data["date_reservation"];
    $heure_debut = $data["heure_debut"];
    $heure_fin = $data["heure_fin"];

    // Vérifier si l'utilisateur existe
    $stmt = $mysqli->prepare("SELECT id FROM users WHERE email = ?");
    $stmt->bind_param("s", $email);
    $stmt->execute();
    $stmt->bind_result($id_user);
    $stmt->fetch();
    $stmt->close();

    if ($id_user) {
        // Mise à jour des infos utilisateur
        $stmt_update = $mysqli->prepare("UPDATE users SET nom = ?, telephone = ? WHERE id = ?");
        $stmt_update->bind_param("ssi", $nom, $telephone, $id_user);
        $stmt_update->execute();
        $stmt_update->close();

        // Mise à jour de la réservation (sur la même date)
        $stmt_res = $mysqli->prepare("UPDATE reservations SET heure_debut = ?, heure_fin = ?, objet = ? WHERE id_user = ? AND date_reservation = ?");
        $stmt_res->bind_param("sssis", $heure_debut, $heure_fin, $objet, $id_user, $date);

        if ($stmt_res->execute()) {
            echo json_encode(["status" => "success", "message" => "Réservation modifiée avec succès"]);
        } else {
            echo json_encode(["status" => "error", "message" => "Erreur modification"]);
        }
        $stmt_res->close();
    } else {
        echo json_encode(["status" => "error", "message" => "Utilisateur introuvable"]);
    }
} elseif ($action === "check_card") {
    $card_uid = $data["card_uid"];

    // Vérifier si la carte est enregistrée dans la table 'cartes'
    $stmt = $mysqli->prepare("SELECT id_user FROM cartes WHERE uid = ?");
    $stmt->bind_param("s", $card_uid);
    $stmt->execute();
    $stmt->bind_result($id_user);
    $stmt->fetch();
    $stmt->close();

    if ($id_user) {
        echo json_encode([
            "status" => "success",
            "message" => "Veuillez réserver un créneau.",
            "action" => "show_calendar"
        ]);
    } else {
        echo json_encode([
            "status" => "error",
            "message" => "Carte non enregistrée"
        ]);
    }
} else {
    echo json_encode(["status" => "error", "message" => "Action non reconnue"]);
}

$mysqli->close();
?>