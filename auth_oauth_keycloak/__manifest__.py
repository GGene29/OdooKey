{
    "name": "Auth OAuth Keycloak",
    "summary": """
        Enables Keycloack integration for the OAuth2 Authentication module.
    """,
    "author": "Mint System, Odoo Community Association (OCA)",
    "website": "https://www.mint-system.ch",
    "license": "AGPL-3",
    "category": "Technical Settings",
    "version": "17.0",
    "depends": ["base", "auth_oauth","auth_signup"],
    "data": ["views/auth_oauth.xml",],
    "images": ["images/screen.png"],
}
