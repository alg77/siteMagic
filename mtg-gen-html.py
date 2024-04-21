from bs4 import BeautifulSoup
import pandas as pd
import requests


def fetch_card_info(card_name):
    """Fetch card editions and prices from Scryfall."""
    url = f"https://api.scryfall.com/cards/search?q={card_name}"
    response = requests.get(url)
    data = response.json()
    cards_info = []

    for card in data.get('data', []):
        cards_info.append({
            'name': card.get('name'),
            'set_name': card.get('set_name'),
            'image_url': card.get('image_urls', {}).get('normal', ''),
            'price_usd': card.get('prices', {}).get('usd', 'N/A'),
            'price_eur': card.get('prices', {}).get('eur', 'N/A'),
            'price': card.get('price')
        })

    return cards_info


def fetch_price_from_playin(url):
    """Fetch card price from Play-in by scraping."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Utilisation de l'attribut itemprop="price" pour trouver le prix
            price_element = soup.find('span', itemprop='price')
            if price_element:
                print(price_element.text.strip() + " €")
                return price_element.text.strip() + " €" # Supprime les espaces superflus et ajoute l'unité monétaire pour clarté
    except Exception as e:
        print(f"Erreur lors de la récupération du prix depuis Play-in : {e}")
    return "N/A"  # Retourne "N/A" si le prix ne peut être récupéré


def generate_html(cards_info):
    """Generate HTML content from card information."""
    html_content = '<html><body><h1>Wishlist Magic: The Gathering</h1>'

    for card in cards_info:
        html_content += f"<div><h2>{card['name']} - {card['set_name']}</h2>"
        if card['image_url']:
            html_content += f"<img src='{card['image_url']}' alt='{card['name']}' style='width:200px;'>"
        html_content += f"<p>Price USD: {card['price_usd']} | Price EUR: {card['price_eur']}</p></div>"

    html_content += '</body></html>'
    return html_content


def generate_html_file_OLD(df, filename="wishlist.html"):
    """Generate an HTML file from the DataFrame."""
    html_content = '<html><head><meta charset="UTF-8"><title>Wishlist Magic: The Gathering</title></head><body><h1>Ma Wishlist Magic: The Gathering</h1>'

    for index, row in df.iterrows():
        price = fetch_price_from_playin(row['Play-in'])
        html_content += f"<div><h2>{row['Carte']}</h2><img src='{row['Image']}' alt='{row['Carte']}' style='width:200px;'><p>Edition: {row['Edition']} | <a href='{row['Play-in']}'>Voir sur Play-in</a> | Prix: {price}</p></div>"

    html_content += '</body></html>'

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Le fichier {filename} a été généré avec succès.")

def generate_html_file(df, html_filename="wishlist.html", css_filename="style.css"):
    """Generate an HTML file with a stylish layout for Magic: The Gathering cards."""
    html_content = f'''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Wishlist Magic: The Gathering</title>
    <link href="https://fonts.googleapis.com/css2?family=Gochi+Hand&family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{css_filename}">
</head>
<body>
    <h1>Ma Wishlist Magic: The Gathering</h1>
    <div class="cards-container">
    '''

    # Ajouter le conteneur pour le pop-up dans le HTML
    html_content += '''
        <div id="popup-img-container" onclick="closePopup()">
            <img id="popup-img" src="" alt="Image agrandie" />
        </div>
        <script>
        function openPopup(src) {
            document.getElementById('popup-img').src = src;
            document.getElementById('popup-img-container').style.display = 'flex';
        }
        function closePopup() {
            document.getElementById('popup-img-container').style.display = 'none';
        }
        </script>
        '''
    for _, row in df.iterrows():
        card_details = get_card_details(row['Play-in'])
        # Assurez-vous que card_details contient bien 'image_url' et 'edition' après appel de la fonction get_card_details
        html_content += f'''
            <div class="card">
                <h2>{row['Carte']}</h2>
                <img src='{card_details['image_url']}' alt='{row['Carte']}' onclick="openPopup('{card_details['image_url']}')"/>
                <p>Edition: {card_details['edition']}<br>
                <a href='{row['Play-in']}'>Voir sur Play-in</a> | Prix: {card_details['price']}</p>
            </div>
            '''
    html_content += '''
    </div>
</body>
</html>
    '''
    # Ajouter le conteneur pour le pop-up dans le HTML
    html_content += '''
        <div id="popup-img-container" onclick="closePopup()">
            <img id="popup-img" src="" alt="Image agrandie" />
        </div>
        <script>
        function openPopup(src) {
            document.getElementById('popup-img').src = src;
            document.getElementById('popup-img-container').style.display = 'flex';
        }
        function closePopup() {
            document.getElementById('popup-img-container').style.display = 'none';
        }
        </script>
        '''
    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Le fichier {html_filename} a été généré avec succès.")


def get_card_details_old(play_in_url):
    """Fonction pour récupérer les détails de la carte."""
    """Récupère les détails d'une carte à partir de son URL sur Play-in."""
    try:
        response = requests.get(play_in_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')


            # Extraction de l'URL de l'image de la carte
            img_container = soup.find('div', class_='illu_card')
            img_element = img_container.find('img') if img_container else None
            img_url = f"https://www.play-in.com{img_element['src']}" if img_element and img_element.has_attr(
                'src') else 'Image non trouvée'

            # Extraction du nom de l'édition de la carte
            edition_container = soup.find('div', class_='illu_ext')
            edition_img = edition_container.find('img') if edition_container else None
            edition_title = edition_img['title'] if edition_img and edition_img.has_attr(
                'title') else 'Édition non trouvée'

            # Utilisation de l'attribut itemprop="price" pour trouver le prix
            price_element = soup.find('span', itemprop='price')
            if price_element:
                print(price_element.text.strip() + " €")
                return price_element.text.strip() + " €" # Supprime les espaces superflus et ajoute l'unité monétaire pour clarté

            return {
                'image_url': img_url,
                'edition': edition_title,
                'price': price_element
            }
    except Exception as e:
        print(f"Erreur lors de la récupération des détails de la carte : {e}")

    return None


def get_card_details(play_in_url):
    """Récupère les détails d'une carte à partir de son URL sur Play-in."""
    try:
        response = requests.get(play_in_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extraction de l'URL de l'image de la carte
            img_container = soup.find('div', class_='illu_card')
            img_element = img_container.find('img') if img_container else None
            img_url = f"https://www.play-in.com{img_element['src']}" if img_element and img_element.has_attr(
                'src') else 'Image non trouvée'

            # Extraction du nom de l'édition de la carte
            edition_container = soup.find('div', class_='illu_ext')
            edition_img = edition_container.find('img') if edition_container else None
            edition_title = edition_img['title'] if edition_img and edition_img.has_attr(
                'title') else 'Édition non trouvée'

            # Extraction du prix de la carte
            price_element = soup.find('span', itemprop='price')
            price = price_element.text.strip() + " €" if price_element else 'Prix non trouvé'

            return {
                'image_url': img_url,
                'edition': edition_title,
                'price': price  # Assurez-vous d'utiliser 'price' ici
            }
    except Exception as e:
        print(f"Erreur lors de la récupération des détails de la carte : {e}")

    return None


# La fonction `update_csv_with_images_and_edition` semble correcte maintenant.

def update_csv_with_images_and_edition(csv_input_path, csv_output_path):
    """Mise à jour du CSV avec les URLs des images et les éditions."""
    df = pd.read_csv(csv_input_path)

    # Initialiser les nouvelles colonnes
    df['Image_URL'] = ''
    df['Edition'] = ''
    df['Prix'] = ''

    for index, row in df.iterrows():
        play_in_url = row['Play-in']
        card_details = get_card_details(play_in_url)
        if card_details:
            df.at[index, 'Image_URL'] = card_details['image_url']
            df.at[index, 'Edition'] = card_details['edition']
            df.at[index, 'Prix'] = card_details['price']
        else:
            print(f"Details not found for card at {play_in_url}")

    df.to_csv(csv_output_path, index=False)
    print(f"CSV updated and saved to {csv_output_path}")



def generate_html_file_from_csv(csv_path, html_filename="wishlist2.html", css_filename="style3.css"):
    """Génère le fichier HTML à partir du CSV mis à jour."""
    df = pd.read_csv(csv_path)

    html_content = f'''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Wishlist Magic : The Gathering</title>
    <link href="https://fonts.googleapis.com/css2?family=Gochi+Hand&family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{css_filename}">
</head>
<body>
    <h1>Ma Wishlist Magic : The Gathering</h1>
    <div class="cards-container">
    '''

    # Ajouter le conteneur pour le pop-up dans le HTML
    html_content += '''
        <div id="popup-img-container" onclick="closePopup()">
            <img id="popup-img" src="" alt="Image agrandie" />
        </div>
        <script>
        function openPopup(src) {
            document.getElementById('popup-img').src = src;
            document.getElementById('popup-img-container').style.display = 'flex';
        }
        function closePopup() {
            document.getElementById('popup-img-container').style.display = 'none';
        }
        </script>
        '''

    prices = []
    for _, row in df.iterrows():
        card_details = get_card_details(row['Play-in'])
        price = fetch_price_from_playin(row['Play-in'])
        prices.append(price)
        row['Price'] = price
        print(f"Prix pour {row['Carte']} sur Play-in : {price}")

        # Assurez-vous que card_details contient bien 'image_url' et 'edition' après appel de la fonction get_card_details
        html_content += f'''
            <div class="card">
                <h2>{row['Carte']}</h2>
                <img src='{card_details['image_url']}' alt='{row['Carte']}' onclick="openPopup('{card_details['image_url']}')"/>
                <p>Edition: {card_details['edition']}<br>
                <a href='{row['Play-in']}'>Voir sur Play-in</a><br>
                Prix: {card_details['price']}</p>
            </div>
            '''
    html_content += '''
    </div>
    '''

    # Ajouter le conteneur pour le pop-up dans le HTML
    html_content += '''
        <div id="popup-img-container" onclick="closePopup()">
            <img id="popup-img" src="" alt="Image agrandie" />
        </div>
        <script>
        function openPopup(src) {
            document.getElementById('popup-img').src = src;
            document.getElementById('popup-img-container').style.display = 'flex';
        }
        function closePopup() {
            document.getElementById('popup-img-container').style.display = 'none';
        }
        </script>
        '''
    html_content += '''
    </body>
    </html>
        '''

    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Le fichier HTML {html_filename} a été généré avec succès.")


# ...

def generate_html_file_from_csv2(csv_path, html_filename="wishlist3.html", css_filename="style3.css"):
    df = pd.read_csv(csv_path)
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Wishlist Magic: The Gathering</title>
        <link href="https://fonts.googleapis.com/css2?family=Gochi+Hand&family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="{css_filename}">
        <style>
            /* Votre CSS ici */
            #popup-img-container {{
                display: none; /* Caché par défaut */
                position: fixed; /* Pour s'afficher par-dessus tout */
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8); /* Fond sombre semi-transparent */
                z-index: 1000; /* S'assurer qu'il est au-dessus des autres éléments */
                justify-content: center;
                align-items: center;
            }}
            #popup-img {{
                max-width: 80%; /* Ajustez en fonction de la taille souhaitée */
                max-height: 80%;
            }}
        </style>
        <script>
            function openPopup(src) {{
                document.getElementById('popup-img').src = src;
                document.getElementById('popup-img-container').style.display = 'flex';
            }}
            function closePopup() {{
                document.getElementById('popup-img-container').style.display = 'none';
            }}
        </script>
    </head>
    <body>
        <h1>Ma Wishlist Magic: The Gathering</h1>
        <div class="cards-container">
    """.format(css_filename=css_filename)

    for _, row in df.iterrows():
        html_content += f'''
        <div class="card">
            <h2>{row['Carte']}</h2>
            <img src='{row['Image_URL']}' alt='{row['Carte']}' onclick="openPopup('{row['Image_URL']}')"/>
            <p>Edition : {row['Edition']}<br>
            <a href='{row['Play-in']}'>Voir sur Play-in</a><br>
            Prix : {row['Prix']}</p>
        </div>
        '''

    html_content += """
    </div>
    <div id="popup-img-container" onclick="closePopup()">
        <img id="popup-img" src="" alt="Image agrandie" />
    </div>
</body>
</html>
    """

    with open(html_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Le fichier HTML {html_filename} a été généré avec succès.")


# Chemin d'accès au CSV d'entrée et de sortie
csv_input_path = 'Magic-cards-vide.csv'
csv_output_path = 'Magic-cards_updated.csv'

# Mise à jour du CSV
update_csv_with_images_and_edition(csv_input_path, csv_output_path)

# Générer le fichier HTML à partir du CSV mis à jour
generate_html_file_from_csv2(csv_output_path)




"""
# Assurez-vous que votre CSV a une colonne 'Play-in' avec les URLs valides
prices = []
for index, row in df.iterrows():
    price = fetch_price_from_playin(row['Play-in'])
    prices.append(price)
    print(f"Prix pour {row['Carte']} sur Play-in : {price}")


# Ajoutez les prix récupérés au DataFrame si nécessaire
df['Prix Play-in'] = prices

# Si vous souhaitez enregistrer les résultats dans un nouveau fichier CSV
df.to_csv('MTG-wishlist-maj.csv', index=False)

print("Mise à jour terminée. Les prix ont été récupérés avec succès.")
all_cards_info = []
for card_name in df['Carte']:
    all_cards_info.extend(fetch_card_info(card_name))

html_content = generate_html(all_cards_info)

# Save the HTML content to a file
with open('wishlist.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("HTML file generated successfully.")
"""
