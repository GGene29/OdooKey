# Copyright 2016 ICTSTUDIO <http://www.ictstudio.eu>
# Copyright 2021 ACSONE SA/NV <https://acsone.eu>
# License: AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
import secrets

import requests
_logger = logging.getLogger(__name__)

from odoo import fields, models, tools

try:
    from jose import jwt
    from jose.exceptions import JWSError, JWTError
except ImportError:
    logging.getLogger(__name__).debug("jose library not installed")


class AuthOauthProvider(models.Model):
    _inherit = "auth.oauth.provider"

    flow = fields.Selection(
        [
            ("access_token", "OAuth2"),
            ("id_token_code", "OpenID Connect (authorization code flow)"),
            ("id_token", "OpenID Connect (implicit flow, not recommended)"),
        ],
        string="Auth Flow",
        required=True,
        default="access_token",
    )
    token_map = fields.Char(
        help="Some Oauth providers don't map keys in their responses "
        "exactly as required.  It is important to ensure user_id and "
        "email at least are mapped. For OpenID Connect user_id is "
        "the sub key in the standard."
    )
    client_secret = fields.Char(
        help="Used in OpenID Connect authorization code flow for confidential clients.",
    )
    code_verifier = fields.Char(
        default=lambda self: secrets.token_urlsafe(32), help="Used for PKCE."
    )
    validation_endpoint = fields.Char(required=False)
    token_endpoint = fields.Char(
        string="Token URL", help="Required for OpenID Connect authorization code flow."
    )
    jwks_uri = fields.Char(string="JWKS URL", help="Required for OpenID Connect.")
    auth_link_params = fields.Char(
        help="Additional parameters for the auth link. "
        "For example: {'prompt':'select_account'}"
    )

    @tools.ormcache("self.jwks_uri", "kid")
    def _get_keys(self, kid):
        r = requests.get(self.jwks_uri, timeout=10)
        _logger.info('\n\n')
        _logger.info('\n\n')
        _logger.info('RESPONSE _________GET KEYS_____________')
        _logger.info(kid)
        r.raise_for_status()
        response = r.json()
        # the keys returned here should follow
        # JWS Notes on Key Selection
        # https://datatracker.ietf.org/doc/html/draft-ietf-jose-json-web-signature#appendix-D
        return [
            key
            for key in response["keys"]
            if kid is None or key.get("kid", None) == kid
        ]

    def _map_token_values(self, res):
        _logger.info('\n\n')
        _logger.info('\n\n')
        _logger.info('RES ______MAP TOKEN ________________')
        _logger.info(self.token_map)
        if self.token_map:
            for pair in self.token_map.split(" "):
                _logger.info('RECORIDO DEL TOKEN')
                _logger.info(pair)
                from_key, to_key = (k.strip() for k in pair.split(":", 1))
                if to_key not in res:
                    res[to_key] = res.get(from_key, "")
        _logger.info('\n\n')
        _logger.info('RETURN MAP')
        _logger.info(res)
        return res

    def _parse_id_token(self, id_token, access_token):
        _logger.info('\n\n')
        _logger.info('\n\n')
        _logger.info('RESPONSE _________parse id token_____________')
        _logger.info(access_token)
        _logger.info(id_token)
        self.ensure_one()
        res = {}
        header = jwt.get_unverified_header(id_token)
        _logger.info('HEADER  --- HEADER')
        _logger.info(header)
        res.update(self._decode_id_token(access_token, id_token, header.get("kid")))
        res.update(self._map_token_values(res))
        _logger.info('\n\n')
        _logger.info('RETURN PARSE TOKEN')
        _logger.info(res)
        return res

    def _decode_id_token(self, access_token, id_token, kid):
        keys = self._get_keys(kid)
        if len(keys) > 1 and kid is None:
            # https://openid.net/specs/openid-connect-core-1_0.html#rfc.section.10.1
            # If there are multiple keys in the referenced JWK Set document, a kid
            # value MUST be provided in the JOSE Header.
            raise JWTError(
                "OpenID Connect requires kid to be set if there is more"
                " than one key in the JWKS"
            )
        error = None
        # we accept multiple keys with the same kid in case a key gets rotated.
        for key in keys:
            try:
                values = jwt.decode(
                    id_token,
                    key,
                    algorithms=["RS256"],
                    audience=self.client_id,
                    access_token=access_token,
                )
                return values
            except (JWTError, JWSError) as e:
                error = e
        if error:
            raise error
        return {}
