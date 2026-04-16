import gradio as gr

# Handpicked best shopping platforms with fixed logo URLs
shopping_platforms = [
    {
        "name": "Amazon",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
        "description": "Wide range of products from fashion to electronics. Great deals and fast delivery.",
        "link": "https://www.amazon.in",
        "category": "Tech, Fashion",
        "badges": ["Top Pick"]
    },
    {
        "name": "Flipkart",
        "logo": "https://1000logos.net/wp-content/uploads/2021/02/Flipkart-logo.png",
        "description": "India's homegrown online store with massive selection in electronics, fashion, and more.",
        "link": "https://www.flipkart.com",
        "category": "Tech, Fashion"
    },
    {
        "name": "Myntra",
        "logo": "https://1000logos.net/wp-content/uploads/2022/08/Myntra-Logo.png",
        "description": "Trendy fashion store featuring top brands and styles for all genders.",
        "link": "https://www.myntra.com",
        "category": "Fashion"
    },
    {
        "name": "Meesho",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/8/80/Meesho_Logo_Full.png",
        "description": "Affordable lifestyle and fashion products, loved by resellers.",
        "link": "https://www.meesho.com",
        "category": "Fashion"
    },
    {
        "name": "Zara",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/f/fd/Zara_Logo.svg",
        "description": "Global high-street fashion brand known for stylish collections.",
        "link": "https://www.zara.com/in/",
        "category": "Fashion"
    },
    {
        "name": "H&M",
        "logo": "https://upload.wikimedia.org/wikipedia/commons/5/53/H%26M-Logo.svg",
        "description": "Modern, sustainable fashion for men, women, and kids.",
        "link": "https://www2.hm.com/en_in/index.html",
        "category": "Fashion"
    },
        {
        "name": "Ajio",
        "logo": "https://assets.ajio.com/static/img/Ajio-Logo.svg",
        "description": "Stylish online platform for curated fashion collections.",
        "link": "https://www.ajio.com",
        "category": "Fashion"
    },
    {
        "name": "Nykaa Fashion",
        "logo": "https://cdn.brandfetch.io/idX52qgqrL/w/668/h/667/theme/dark/icon.jpeg?c=1dxbfHSJFAPEGdCLU4o5B",
        "description": "Premium fashion and beauty destination for modern women.",
        "link": "https://www.nykaafashion.com",
        "category": "Beauty, Fashion"
    },
    {
        "name": "Tata CLiQ",
        "logo": "https://cdn.brandfetch.io/idRILRSTEh/w/400/h/400/theme/dark/icon.jpeg?c=1bxid64Mup7aczewSAYMX&t=1724233384745​",
        "description": "Tata Group’s official store for electronics, fashion and lifestyle.",
        "link": "https://www.tatacliq.com",
        "category": "Tech, Fashion"
    },
    {
        "name": "Urbanic",
        "logo": "https://cdn.brandfetch.io/idH5bdraWS/w/180/h/180/theme/dark/logo.png?c=1bxid64Mup7aczewSAYMX&t=1740645476824",
        "description": "Fashion-forward, Instagram-ready trends for Gen Z.",
        "link": "https://www.urbanic.com/in",
        "category": "Fashion"
    },
    {
        "name": "Snapdeal",
        "logo": "https://cdn.brandfetch.io/idJGV0ytrh/w/400/h/400/theme/dark/icon.jpeg?c=1bxid64Mup7aczewSAYMX&t=1740723635644",
        "description": "Value-driven online marketplace for everything affordable.",
        "link": "https://www.snapdeal.com",
        "category": "Tech, Fashion"
    },
    {
        "name": "Zivame",
        "logo": "https://cdn.brandfetch.io/id6s-JM6qh/w/400/h/400/theme/dark/icon.png?c=1bxid64Mup7aczewSAYMX&t=1740645830248",
        "description": "India’s top destination for innerwear, activewear, and lingerie.",
        "link": "https://www.zivame.com",
        "category": "Fashion, Beauty"
    },
    {
        "name": "Decathlon",
        "logo": "https://cdn.brandfetch.io/idoZAes0Vb/w/667/h/667/theme/dark/icon.jpeg?c=1bxid64Mup7aczewSAYMX&t=1727714573401​",
        "description": "Everything sports: fitness gear, apparel, and accessories.",
        "link": "https://www.decathlon.in",
        "category": "Sports, Tech",
        "badges": "TopPick"
    },
    {
    "name": "Croma",
    "logo": "https://cdn.brandfetch.io/id9J1O8vnD/w/351/h/138/theme/dark/logo.png?c=1bxid64Mup7aczewSAYMX&t=1740734375309",
    "description": "Tata-owned electronics and appliances megastore with great offline + online experience.",
    "link": "https://www.croma.com",
    "category": "Tech"
    },
    {
    "name": "Calvin Klein",
    "logo": "https://cdn.brandfetch.io/idaY88zIWD/w/1440/h/1440/theme/dark/icon.jpeg?c=1bxid64Mup7aczewSAYMX&t=1742470968402",
    "description": "Minimalist American fashion house known for modern styles, denim, and iconic underwear.",
    "link": "https://www.calvinklein.in/",
    "category": "Fashion",
    "badges": ["Luxury"]
    },
    {
    "name": "Chanel",
    "logo": "https://cdn.brandfetch.io/idBUm3gJdJ/theme/dark/symbol.svg?c=1bxid64Mup7aczewSAYMX&t=1741582517907",
    "description": "Iconic French luxury brand known for timeless elegance, haute couture, and perfumes.",
    "link": "https://www.chanel.com/in/",
    "category": "Fashion, Beauty",
    "badges": ["Luxury", "Top Pick"]
    },
    {
    "name": "Gucci",
    "logo": "https://cdn.brandfetch.io/idsVLhORjl/w/400/h/400/theme/dark/icon.jpeg?c=1bxid64Mup7aczewSAYMX&t=1731307354354",
    "description": "Italian luxury house blending fashion heritage with bold, contemporary designs.",
    "link": "https://www.gucci.com/in/en/",
    "category": "Fashion",
    "badges": ["Luxury"]
    },
    {
    "name": "Dior",
    "logo": "https://cdn.brandfetch.io/id26xlFDgU/w/400/h/400/theme/dark/icon.jpeg?c=1bxid64Mup7aczewSAYMX&t=1675924240987",
    "description": "French powerhouse in couture and beauty, setting global trends since 1946.",
    "link": "https://www.dior.com/en_int",
    "category": "Fashion, Beauty",
    "badges": ["Luxury"]
    },

    {
    "name": "Louis Vuitton",
    "logo": "https://cdn.brandfetch.io/idQH6e1xMu/w/400/h/400/theme/dark/icon.jpeg?c=1bxid64Mup7aczewSAYMX&t=1676549440779",
    "description": "Legendary brand for leather goods, fashion, and luxury lifestyle products.",
    "link": "https://www.louisvuitton.com",
    "category": "Fashion",
    "badges": ["Luxury"]
    }

]



# Render HTML in grid layout with category filter
def render_platforms(category_filter="All"):
    html = """
    <style>
        .platform-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
            padding: 10px;
        }

        .platform-card {
            flex: 1 1 300px;
            min-width: 280px;
            border: 1px solid #ccc;
            padding: 20px;
            border-radius: 15px;
            background: white;
            transition: transform 0.4s ease, box-shadow 0.3s ease, background 0.5s;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            position: relative;
            animation: fadeInUp 0.5s ease forwards;
        }

        .platform-card:hover {
    transform: translateY(-40px) scale(1.05); /* Dramatic lift and slight scale */
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3); /* Stronger shadow */
    z-index: 5;
}



        .platform-card.luxury {
            background: linear-gradient(135deg, #fef5ff, #f4eaff);
            border: 1px solid #d1b3ff;
        }

        .platform-card img {
            transition: transform 0.3s ease-in-out;
            margin-bottom: 10px;
        }

        .platform-card:hover img {
            transform: scale(1.1);
        }

        .badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 8px;
            font-size: 12px;
            color: white;
            margin-right: 6px;
            animation: floatGlow 2.5s ease-in-out infinite;
            box-shadow: 0 0 8px rgba(255, 255, 255, 0.6);
        }

        .badge.top { background-color: #ffc107; }
        .badge.luxury { background-color: #c084fc; }
        .badge.green { background-color: #28a745; }

        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.08); opacity: 0.85; }
        }

        @keyframes fadeInUp {
            0% {
                opacity: 0;
                transform: translateY(30px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes floatGlow {
            0% {
                transform: translateY(0px);
                box-shadow: 0 0 8px rgba(255, 255, 255, 0.4);
            }
            50% {
                transform: translateY(-3px);
                box-shadow: 0 0 12px rgba(255, 255, 255, 0.8);
            }
            100% {
                transform: translateY(0px);
                box-shadow: 0 0 8px rgba(255, 255, 255, 0.4);
            }
        }

        .visit-btn {
            color: white;
            background: linear-gradient(135deg, #007bff, #0056b3);
            padding: 10px 16px;
            text-decoration: none;
            border-radius: 6px;
            display: inline-block;
            transition: all 0.3s ease;
            margin-top: 10px;
        }

        .visit-btn:hover {
            background: linear-gradient(135deg, #0056b3, #003d80);
            transform: scale(1.05);
            box-shadow: 0 0 10px rgba(0, 123, 255, 0.4);
        }

    </style>
    <div class='platform-grid'>
    """

    large_logos = ["nykaa fashion", "tata cliq", "louis vuitton", "calvin klein"]

    for platform in shopping_platforms:
        if category_filter != "All" and category_filter.lower() not in platform["category"].lower():
            continue

        logo_style = "max-height: 100px;" if platform["name"].lower() in large_logos else "max-height: 60px;"

        badges_html = ""
        has_luxury = False
        if "badges" in platform:
            for badge in platform["badges"]:
                class_name = "top" if badge == "Top Pick" else "luxury" if badge == "Luxury" else "green"
                badges_html += f"<span class='badge {class_name}'>{badge}</span>"
                if badge == "Luxury":
                    has_luxury = True

        card_class = "platform-card luxury" if has_luxury else "platform-card"

        html += f"""
        <div class='{card_class}'>
            <img src='{platform["logo"]}' alt='{platform["name"]} Logo' style='{logo_style}'><br>
            <h3 style='margin: 5px 0;'>{platform["name"]}</h3>
            {badges_html}
            <p style='font-size: 14px; color: #333;'>{platform["description"]}</p>
            <p style='font-size: 12px; color: gray;'>Category: {platform["category"]}</p>
            <a href='{platform["link"]}' target='_blank'
            style='
                    color: white;
                    background-color: #007bff;
                    padding: 10px 16px;
                    font-weight: 600;
                    font-size: 14px;
                    border-radius: 5px;
                    text-decoration: none;
                    margin-top: 10px;
                    display: inline-block;
                    transition: background 0.3s ease, transform 0.3s ease;
                    onmouseover="this.style.backgroundColor='#0056b3'; this.style.transform='scale(1.05)';"
                    onmouseout="this.style.backgroundColor='#007bff'; this.style.transform='scale(1)';">Visit</a>

        </div>
        """

    html += "</div>"
    return html

# Gradio interface
with gr.Blocks() as platform_interface:
    gr.Markdown("## ✨ Discover the Best Shopping Platforms")
    category = gr.Dropdown(choices=["All", "Fashion", "Beauty", "Tech", "Sports"], value="All", label="Filter by Category")
    output_html = gr.HTML()

    category.change(fn=render_platforms, inputs=category, outputs=output_html)
    output_html.value = render_platforms("All")
