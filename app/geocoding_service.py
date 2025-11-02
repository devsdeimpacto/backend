import httpx
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class GeocodingService:
    """
    Serviço de geocodificação usando a API do Nominatim
    do OpenStreetMap.
    """

    BASE_URL = "https://nominatim.openstreetmap.org"

    @staticmethod
    async def geocode_address(
        endereco: str,
        timeout: float = 10.0
    ) -> Optional[Dict[str, float]]:
        """
        Converte um endereço em coordenadas (latitude, longitude).

        Args:
            endereco: Endereço completo para geocodificar
            timeout: Tempo máximo de espera pela resposta (segundos)

        Returns:
            Dict com 'latitude' e 'longitude' ou None se não encontrar
        """
        try:
            # Formata os parâmetros da requisição
            params = {
                "q": endereco,
                "format": "json",
                "limit": 1,
                "addressdetails": 0
            }

            # Headers recomendados pela API do Nominatim
            headers = {
                "User-Agent": "DevsDeImpacto-Backend/1.0"
            }

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    f"{GeocodingService.BASE_URL}/search",
                    params=params,
                    headers=headers
                )
                response.raise_for_status()

                data = response.json()

                if data and len(data) > 0:
                    primeiro_resultado = data[0]
                    return {
                        "latitude": float(
                            primeiro_resultado.get("lat")
                        ),
                        "longitude": float(
                            primeiro_resultado.get("lon")
                        )
                    }

                logger.warning(
                    f"Nenhuma coordenada encontrada para: {endereco}"
                )
                return None

        except httpx.TimeoutException:
            logger.error(
                f"Timeout ao geocodificar endereço: {endereco}"
            )
            return None
        except httpx.HTTPError as e:
            logger.error(
                f"Erro HTTP ao geocodificar endereço: {endereco}. "
                f"Erro: {e}"
            )
            return None
        except (ValueError, KeyError) as e:
            logger.error(
                f"Erro ao processar resposta da geocodificação: {e}"
            )
            return None
        except Exception as e:
            logger.error(
                f"Erro inesperado ao geocodificar: {e}"
            )
            return None

