"""
oTree websocket gonderim yamasi                                           16 Kasim 2026

SORUN (py-spy ile kanitlandi): oTree'nin ChannelLayer.sync_send metodu, istek is parcaciginda
asyncio.run() ile YENI bir olay dongusu acip ana donguye ait websocket'lere yaziyor.
Windows + Python 3.14'te bu cagri sonsuza kadar takilabiliyor; global kilit tutuldugu icin
butun sunucu donuyor (13 ve 16 Kasim takilmalari).

YAMA: Is parcaciginda yeni dongu acmak yerine, mesaji ana olay dongusune
run_coroutine_threadsafe ile birakir (ates et ve unut). Websocket'e yazma islemi artik
kendi dongusunde yapilir; istek parcacigi hicbir seyi beklemez.

Yan etki yok: ayni mesajlar ayni gruplara gider. Hic websocket baglanmamissa
(ana dongu henuz bilinmiyorsa) gonderilecek kimse de yoktur.
"""
import asyncio
import otree.channels.utils as _cu

if not getattr(_cu.ChannelLayer, '_kanal_yama_uygulandi', False):
    _orig_add = _cu.ChannelLayer.add

    def _add(self, group, websocket):
        try:
            self._main_loop = asyncio.get_running_loop()
        except RuntimeError:
            pass
        return _orig_add(self, group, websocket)

    def _sync_send(self, group, data):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            loop = getattr(self, '_main_loop', None)
            if loop is not None and loop.is_running():
                asyncio.run_coroutine_threadsafe(self.send(group, data), loop)
            return
        asyncio.create_task(self.send(group, data))

    _cu.ChannelLayer.add = _add
    _cu.ChannelLayer.sync_send = _sync_send
    _cu.ChannelLayer._kanal_yama_uygulandi = True
