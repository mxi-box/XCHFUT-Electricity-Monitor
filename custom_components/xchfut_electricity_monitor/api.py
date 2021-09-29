import re
import json
import aiohttp
import asyncio

from yarl import URL
from typing import Union
from homeassistant.exceptions import HomeAssistantError
from .const import API_ACCOUNT_ID
from .const import API_SERVER_URL


balance_matcher = re.compile(r'(?<=剩余金额:)[\d]+[.][\d]*')
electri_url = URL("/web/Common/Tsm.html")


class XCHFUTApi() :

    def __init__(self, accountid : str, server : Union[str, URL]):
        if not isinstance(server, URL):
            server = URL(server)
        self.accountid = accountid
        self.full_electri_url = server.join(electri_url)
        self.http_sess = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.http_sess.close()

    def __del__(self):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.session.close())
            else:
                loop.run_until_complete(self.session.close())
        except Exception:
            pass
    
    async def query_electricity_deposite(self, roomid : str) -> str:
        json_data = {
            "query_elec_roominfo": {
                'aid': '0030000000007301',
                'account': self.accountid,
                'room': {
                    'roomid': roomid,
                    'room': roomid
                },
                'floor': {
                    'floorid': '',
                    'floor': ''
                },
                'area': {
                    'area': '',
                    'areaname': ''
                },
                'building': {
                    'buildingid': '',
                    'building': ''
                }
            }
        }
        
        query = {
            'jsondata': json.dumps(json_data),
            'funname': 'synjones.onecard.query.elec.roominfo',
            'json': 'true'
        }

        try:

            async with self.http_sess.post(self.full_electri_url, data=query) as r:
                try:
                    response = await r.json(content_type=None)
                    code = response['query_elec_roominfo']['retcode']
                    msg = response['query_elec_roominfo']['errmsg']
                except Exception:
                    raise FetchFail()

                if code == '0':
                    StrResult = balance_matcher.search(msg).group()
                    return StrResult
                else:
                    raise FetchFail()

        except Exception:
            raise ConnectFail()


class ConnectFail(HomeAssistantError) :
    pass

class FetchFail(HomeAssistantError) :
    pass


api = XCHFUTApi(API_ACCOUNT_ID, API_SERVER_URL)