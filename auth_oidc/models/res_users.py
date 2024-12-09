# Copyright 2016 ICTSTUDIO <http://www.ictstudio.eu>
# Copyright 2021 ACSONE SA/NV <https://acsone.eu>
# License: AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

import requests

from odoo import api, models
from odoo.exceptions import AccessDenied
from odoo.http import request

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    def _auth_oauth_get_tokens_implicit_flow(self, oauth_provider, params):
        _logger.info('\n\n')
        _logger.info('PRIMER METODO GET TOKEN')
        _logger.info(oauth_provider)
        _logger.info(params)
        # https://openid.net/specs/openid-connect-core-1_0.html#ImplicitAuthResponse
        return params.get("access_token"), params.get("id_token")

    def _auth_oauth_get_tokens_auth_code_flow(self, oauth_provider, params):
        # https://openid.net/specs/openid-connect-core-1_0.html#AuthResponse
        code = params.get("code")
        _logger.info('\n\n')
        _logger.info('\n\n')
        _logger.info('OAUTH PROVIDER BASE')
        _logger.info(oauth_provider)
        # https://openid.net/specs/openid-connect-core-1_0.html#TokenRequest
        auth = None
        if oauth_provider.client_secret:
            auth = (oauth_provider.client_id, oauth_provider.client_secret)
            _logger.info('\n\n')
            # _logger.info(oauth_provider.token_endpoint)
            _logger.info('\n\n')
            _logger.info('SI VIENE EL CLIENTE SE ARMA LA TUPLA')
            _logger.info(auth)
        response = requests.post(
            oauth_provider.token_endpoint,
            data=dict(
                client_id=oauth_provider.client_id,
                client_secret=oauth_provider.client_secret,
                grant_type="authorization_code",
                code=code,
                code_verifier=oauth_provider.code_verifier,  # PKCE
                # redirect_uri = "http://localhost:8094/auth_oauth/signin"
                redirect_uri=request.httprequest.url_root + "auth_oauth/signin",
            ),
            auth=auth,
            timeout=10,
        )
        _logger.info('\n\n')
        _logger.info('\n\n')
        _logger.info('RESPONSE 1')
        #_logger.info(response.data)   
        _logger.info('RESPONSE')
        _logger.info(response)
        
        response.raise_for_status()
        response_json = response.json()
        _logger.info('RESPONSE3')
        _logger.info(response_json)
        # https://openid.net/specs/openid-connect-core-1_0.html#TokenResponse
        return response_json.get("access_token"), response_json.get("id_token")

    @api.model
    def auth_oauth(self, provider, params):
        oauth_provider = self.env["auth.oauth.provider"].browse(provider)
        _logger.info('\n\n')
        _logger.info('METODO AUTH OAUTH INIT')
        if oauth_provider.flow == "id_token":
            access_token, id_token = self._auth_oauth_get_tokens_implicit_flow(
                oauth_provider, params
            )
        elif oauth_provider.flow == "id_token_code":
            access_token, id_token = self._auth_oauth_get_tokens_auth_code_flow(
                oauth_provider, params
            )
        else:
            _logger.info('############# retur super oauth')
            return super().auth_oauth(provider, params)
        if not access_token:
            _logger.info('\n\n')
            _logger.info('SIN ACCESO POR acces_token')
            _logger.error("No access_token in response.")
            raise AccessDenied()
        if not id_token:
            _logger.info('\n\n')
            _logger.info('SIN ACCESO POR id del token')
            _logger.error("No id_token in response.")
            raise AccessDenied()
        validation = oauth_provider._parse_id_token(id_token, access_token)
        _logger.info('\n\n')
        _logger.info('VALIDATION --> ')
        _logger.info(validation)
        # required check
        if "sub" in validation and "user_id" not in validation:
            # set user_id for auth_oauth, user_id is not an OpenID Connect standard
            # claim:
            # https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims
            validation["user_id"] = validation["sub"]

        elif not validation.get("user_id"):
            _logger.info('\n\n')
            _logger.info('SIN ACCESO POR validation')
            _logger.error("user_id claim not found in id_token (after mapping).")
            raise AccessDenied()
        # retrieve and sign in user
        params["access_token"] = access_token
        # Creación del login "Contacto"
        login = self._auth_oauth_signin(provider, validation, params)
        _logger.info('\n\n')
        _logger.info('RETURN LOGIN')
        _logger.info(login)
        if not login:
            _logger.info('\n\n')
            _logger.info('SIN ACCESO POR LOGIN')
            raise AccessDenied()
        # return user credentials
        _logger.info('\n\n')
        _logger.info('RETURN DE LOGIN ULTIMO')
        _logger.info(login)
        return (self.env.cr.dbname, login, access_token)
