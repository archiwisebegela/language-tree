import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramBadRequest

# O token é lido da variável de ambiente BOT_TOKEN (seguro para o GitHub)
BOT_TOKEN = os.getenv("BOT_TOKEN", "SEU_TOKEN_AQUI")

# Níveis de vitalidade das línguas (Classificação da UNESCO)
STATUS = {
    "SAFE": "🟢 Segura / Viva (Não ameaçada)",
    "VULNERABLE": "🟡 Vulnerável",
    "ENDANGERED": "🟠 Em perigo",
    "CRITICALLY": "🔴 Criticamente em perigo",
    "REVIVED": "🔵 Revitalizada (Viva)",
    "DEAD": "⚫ Extinta / Morta",
    "LITURGICAL": "🟣 Extinta (Preservada como língua litúrgica)"
}

LANGUAGE_TREE = {
    "root": {
        "name": "🌳 Árvore das Famílias Linguísticas do Mundo",
        "type": "Raiz",
        "regions": "Mundo inteiro",
        "speakers": "~8 mil milhões de pessoas (mais de 7.000 línguas)",
        "info": "Selecione uma das principais famílias linguísticas para explorar os seus ramos, subgrupos e idiomas.",
        "parent": None,
        "children": ["ie", "st", "aa", "ur", "turk"]
    },

    # ================= 1. FAMÍLIA INDO-EUROPEIA =================
    "ie": {
        "name": "🌐 Família Indo-Europeia",
        "type": "Família linguística",
        "regions": "Europa, Américas, Austrália, Sul e Oeste da Ásia",
        "speakers": "~3,3 mil milhões de pessoas",
        "info": "A maior família linguística do mundo em número de falantes.",
        "parent": "root",
        "children": ["ie_ital", "ie_germ", "ie_slav", "ie_anat"]
    },

    # Ramo Itálico / Românico
    "ie_ital": {
        "name": "🌿 Ramo Itálico (Línguas Românicas)",
        "type": "Ramo",
        "regions": "Sul e Oeste da Europa, América Latina, partes da África",
        "speakers": "~900 milhões de pessoas",
        "parent": "ie",
        "children": ["lang_pt", "lang_es", "lang_lat", "lang_sc", "lang_dlm"]
    },
    "lang_pt": {
        "name": "🗣 Português",
        "type": "Língua",
        "regions": "Brasil, Portugal, Angola, Moçambique, Cabo Verde, Guiné-Bissau, São Tomé e Príncipe, Timor-Leste, Macau",
        "speakers": "~260 milhões ( ~235 milhões como língua materna)",
        "status": STATUS["SAFE"],
        "parent": "ie_ital",
        "children": []
    },
    "lang_es": {
        "name": "🗣 Espanhol (Castelhano)",
        "type": "Língua",
        "regions": "Espanha, América Hispânica, Estados Unidos, Guiné Equatorial",
        "speakers": "~595 milhões (~485 milhões como língua materna)",
        "status": STATUS["SAFE"],
        "parent": "ie_ital",
        "children": []
    },
    "lang_lat": {
        "name": "📜 Latim",
        "type": "Língua ancestral",
        "regions": "Roma Antiga / Vaticano",
        "speakers": "0 (como língua materna); usado na ciência e na Igreja Católica",
        "status": STATUS["LITURGICAL"],
        "parent": "ie_ital",
        "children": []
    },
    "lang_sc": {
        "name": "🗣 Sardo",
        "type": "Língua",
        "regions": "Itália (Ilha da Sardenha)",
        "speakers": "~1 milhão de pessoas",
        "status": STATUS["ENDANGERED"],
        "parent": "ie_ital",
        "children": []
    },
    "lang_dlm": {
        "name": "📜 Dálmata",
        "type": "Língua",
        "regions": "Costa do Mar Adriático (Croácia e Montenegro)",
        "speakers": "0 (o último falante, Tuone Udaina, morreu em 1898)",
        "status": STATUS["DEAD"],
        "parent": "ie_ital",
        "children": []
    },

    # Ramo Germânico
    "ie_germ": {
        "name": "🌿 Ramo Germânico",
        "type": "Ramo",
        "regions": "Europa Ocidental e do Norte, América do Norte, Oceania, África do Sul",
        "speakers": "~515 milhões (materna), mais de 1,5 mil milhões (total)",
        "parent": "ie",
        "children": ["germ_west", "germ_east"]
    },
    "germ_west": {
        "name": "🍃 Subgrupo Germânico Ocidental",
        "type": "Subgrupo",
        "regions": "Reino Unido, EUA, Alemanha, Áustria, Suíça, Países Baixos, Canadá, Austrália",
        "speakers": "~490 milhões (língua materna)",
        "parent": "ie_germ",
        "children": ["lang_en", "lang_de", "lang_yi"]
    },
    "lang_en": {
        "name": "🗣 Inglês",
        "type": "Língua",
        "regions": "Mundo inteiro (EUA, Reino Unido, Canadá, Austrália, etc.)",
        "speakers": "~1,45 mil milhões (~380 milhões como língua materna)",
        "status": STATUS["SAFE"],
        "parent": "germ_west",
        "children": []
    },
    "lang_de": {
        "name": "🗣 Alemão",
        "type": "Língua",
        "regions": "Alemanha, Áustria, Suíça, Luxemburgo, Liechtenstein",
        "speakers": "~130 milhões (~95 milhões como língua materna)",
        "status": STATUS["SAFE"],
        "parent": "germ_west",
        "children": []
    },
    "lang_yi": {
        "name": "🗣 Iídiche",
        "type": "Língua",
        "regions": "Israel, EUA, historicamente na Europa Central e Oriental",
        "speakers": "~600.000 pessoas",
        "status": STATUS["ENDANGERED"],
        "parent": "germ_west",
        "children": []
    },
    "germ_east": {
        "name": "🍃 Subgrupo Germânico Oriental",
        "type": "Subgrupo",
        "regions": "Historicamente: Europa Oriental, Itália, Península Ibérica, Crimeia",
        "speakers": "0 pessoas",
        "status": STATUS["DEAD"],
        "parent": "ie_germ",
        "children": ["lang_got"]
    },
    "lang_got": {
        "name": "📜 Gótico",
        "type": "Língua",
        "regions": "Reinos Visigótico e Ostrogótico (o gótico da Crimeia sobreviveu até ao séc. XVIII)",
        "speakers": "0 pessoas",
        "status": STATUS["DEAD"],
        "parent": "germ_east",
        "children": []
    },

    # Ramo Eslavo
    "ie_slav": {
        "name": "🌿 Ramo Eslavo",
        "type": "Ramo",
        "regions": "Europa Oriental, Central e Meridional, Norte da Ásia",
        "speakers": "~315 milhões de pessoas",
        "parent": "ie",
        "children": ["slav_east", "slav_west", "slav_south"]
    },
    "slav_east": {
        "name": "🍃 Subgrupo Eslavo Oriental",
        "type": "Subgrupo",
        "regions": "Europa Oriental, Norte da Ásia",
        "speakers": "~210 milhões de pessoas",
        "parent": "ie_slav",
        "children": ["lang_ru", "lang_uk", "lang_be", "lang_orv"]
    },
    "lang_ru": {
        "name": "🗣 Russo",
        "type": "Língua",
        "regions": "Rússia, Europa Oriental, Ásia Central",
        "speakers": "~255 milhões (~150 milhões como língua materna)",
        "status": STATUS["SAFE"],
        "parent": "slav_east",
        "children": []
    },
    "lang_uk": {
        "name": "🗣 Ucraniano",
        "type": "Língua",
        "regions": "Ucrânia, diásporas na Europa, Canadá e EUA",
        "speakers": "~40–45 milhões de pessoas",
        "status": STATUS["SAFE"],
        "parent": "slav_east",
        "children": []
    },
    "lang_be": {
        "name": "🗣 Bielorrusso",
        "type": "Língua",
        "regions": "Bielorrússia, Polónia (Podláquia)",
        "speakers": "~5–7 milhões (uso diário ativo: 1–2 milhões)",
        "status": STATUS["VULNERABLE"],
        "parent": "slav_east",
        "children": []
    },
    "lang_orv": {
        "name": "📜 Eslavo Oriental Antigo",
        "type": "Língua ancestral",
        "regions": "Europa Oriental (Rus de Kiev)",
        "speakers": "0 (dividiu-se nos séculos XIII–XIV)",
        "status": STATUS["DEAD"],
        "parent": "slav_east",
        "children": []
    },
    "slav_west": {
        "name": "🍃 Subgrupo Eslavo Ocidental",
        "type": "Subgrupo",
        "regions": "Polónia, Chéquia, Eslováquia, Leste da Alemanha (Lusácia)",
        "speakers": "~60 milhões de pessoas",
        "parent": "ie_slav",
        "children": ["lang_pl", "lang_csb", "lang_pox"]
    },
    "lang_pl": {
        "name": "🗣 Polaco (Polonês)",
        "type": "Língua",
        "regions": "Polónia, Lituânia, Bielorrússia, diásporas no Reino Unido e EUA",
        "speakers": "~45 milhões de pessoas",
        "status": STATUS["SAFE"],
        "parent": "slav_west",
        "children": []
    },
    "lang_csb": {
        "name": "🗣 Cassúbio",
        "type": "Língua",
        "regions": "Polónia (Voivodia da Pomerânia)",
        "speakers": "~87.000 pessoas",
        "status": STATUS["ENDANGERED"],
        "parent": "slav_west",
        "children": []
    },
    "lang_pox": {
        "name": "📜 Polábio",
        "type": "Língua",
        "regions": "Nordeste da atual Alemanha (bacia do rio Elba)",
        "speakers": "0 (extinta em 1756)",
        "status": STATUS["DEAD"],
        "parent": "slav_west",
        "children": []
    },
    "slav_south": {
        "name": "🍃 Subgrupo Eslavo Meridional",
        "type": "Subgrupo",
        "regions": "Península Balcânica",
        "speakers": "~30 milhões de pessoas",
        "parent": "ie_slav",
        "children": ["lang_bg", "lang_cu"]
    },
    "lang_bg": {
        "name": "🗣 Búlgaro",
        "type": "Língua",
        "regions": "Bulgária, Ucrânia, Moldávia",
        "speakers": "~8 milhões de pessoas",
        "status": STATUS["SAFE"],
        "parent": "slav_south",
        "children": []
    },
    "lang_cu": {
        "name": "📜 Antigo Eslavo Eclesiástico",
        "type": "Língua",
        "regions": "Balcãs, Europa Oriental",
        "speakers": "0 (usado na liturgia ortodoxa)",
        "status": STATUS["LITURGICAL"],
        "parent": "slav_south",
        "children": []
    },

    # Ramo Anatólico
    "ie_anat": {
        "name": "🌿 Ramo Anatólico",
        "type": "Ramo (extinto)",
        "regions": "Ásia Menor (atual Turquia)",
        "speakers": "0 (extinto na Antiguidade)",
        "status": STATUS["DEAD"],
        "parent": "ie",
        "children": ["lang_hit"]
    },
    "lang_hit": {
        "name": "📜 Hitita",
        "type": "Língua",
        "regions": "Império Hitita (Anatólia Central)",
        "speakers": "0 (a língua indo-europeia escrita mais antiga, séc. XVII–XII a.C.)",
        "status": STATUS["DEAD"],
        "parent": "ie_anat",
        "children": []
    },

    # ================= 2. FAMÍLIA SINO-TIBETANA =================
    "st": {
        "name": "🌐 Família Sino-Tibetana",
        "type": "Família linguística",
        "regions": "Leste, Sudeste e Sul da Ásia",
        "speakers": "~1,4 mil milhões de pessoas",
        "info": "A segunda maior família linguística do mundo em número de falantes.",
        "parent": "root",
        "children": ["st_sinitic", "st_tb"]
    },
    "st_sinitic": {
        "name": "🌿 Ramo Sinítico (Chinês)",
        "type": "Ramo",
        "regions": "China, Taiwan, Singapura",
        "speakers": "~1,35 mil milhões de pessoas",
        "parent": "st",
        "children": ["lang_zh", "lang_yue"]
    },
    "lang_zh": {
        "name": "🗣 Chinês Mandarim",
        "type": "Língua",
        "regions": "China, Taiwan, Singapura",
        "speakers": "~1,1 mil milhões (~940 milhões como língua materna)",
        "status": STATUS["SAFE"],
        "parent": "st_sinitic",
        "children": []
    },
    "lang_yue": {
        "name": "🗣 Cantonês (Yue)",
        "type": "Língua",
        "regions": "Hong Kong, Macau, Província de Guangdong (China)",
        "speakers": "~85 milhões de pessoas",
        "status": STATUS["SAFE"],
        "parent": "st_sinitic",
        "children": []
    },
    "st_tb": {
        "name": "🌿 Ramo Tibeto-Birmanês",
        "type": "Ramo",
        "regions": "Tibete, Mianmar, Butão, Nepal, Nordeste da Índia",
        "speakers": "~60 milhões de pessoas",
        "parent": "st",
        "children": ["lang_my", "lang_txg"]
    },
    "lang_my": {
        "name": "🗣 Birmanês",
        "type": "Língua",
        "regions": "Mianmar (Birmânia)",
        "speakers": "~43 milhões de pessoas",
        "status": STATUS["SAFE"],
        "parent": "st_tb",
        "children": []
    },
    "lang_txg": {
        "name": "📜 Tangute",
        "type": "Língua",
        "regions": "Império Xia Ocidental (Noroeste da China)",
        "speakers": "0 (extinta no século XVI)",
        "status": STATUS["DEAD"],
        "parent": "st_tb",
        "children": []
    },

    # ================= 3. FAMÍLIA AFRO-ASIÁTICA =================
    "aa": {
        "name": "🌐 Família Afro-Asiática",
        "type": "Família linguística",
        "regions": "Norte e Leste da África, Médio Oriente",
        "speakers": "~500 milhões de pessoas",
        "parent": "root",
        "children": ["aa_sem", "aa_eg"]
    },
    "aa_sem": {
        "name": "🌿 Ramo Semítico",
        "type": "Ramo",
        "regions": "Médio Oriente, Norte da África, Etiópia",
        "speakers": "~400 milhões de pessoas",
        "parent": "aa",
        "children": ["lang_ar", "lang_he", "lang_akk"]
    },
    "lang_ar": {
        "name": "🗣 Árabe",
        "type": "Macrolíngua",
        "regions": "Médio Oriente e Norte da África (22 países)",
        "speakers": "~380 milhões de pessoas",
        "status": STATUS["SAFE"],
        "parent": "aa_sem",
        "children": []
    },
    "lang_he": {
        "name": "🗣 Hebraico",
        "type": "Língua",
        "regions": "Israel, comunidades judaicas pelo mundo",
        "speakers": "~9 milhões de pessoas",
        "status": STATUS["REVIVED"],
        "info": "O único exemplo histórico de revitalização completa de uma língua morta como idioma oficial e falado.",
        "parent": "aa_sem",
        "children": []
    },
    "lang_akk": {
        "name": "📜 Acádio (Assírio-Babilónico)",
        "type": "Língua",
        "regions": "Antiga Mesopotâmia",
        "speakers": "0 (extinta no século I d.C.)",
        "status": STATUS["DEAD"],
        "parent": "aa_sem",
        "children": []
    },
    "aa_eg": {
        "name": "🌿 Ramo Egípcio",
        "type": "Ramo",
        "regions": "Egito (Vale do Nilo)",
        "speakers": "0 (no quotidiano)",
        "parent": "aa",
        "children": ["lang_cop"]
    },
    "lang_cop": {
        "name": "📜 Copta",
        "type": "Língua",
        "regions": "Egito",
        "speakers": "0 (deixou de ser língua materna no séc. XVII; usada na Igreja Copta)",
        "status": STATUS["LITURGICAL"],
        "parent": "aa_eg",
        "children": []
    },

    # ================= 4. FAMÍLIA URÁLICA =================
    "ur": {
        "name": "🌐 Família Urálica",
        "type": "Família linguística",
        "regions": "Norte e Centro da Europa, Região do Volga, Urais, Sibéria Ocidental",
        "speakers": "~25 milhões de pessoas",
        "parent": "root",
        "children": ["ur_fu", "ur_sam"]
    },
    "ur_fu": {
        "name": "🌿 Ramo Fino-Úgrico",
        "type": "Ramo",
        "regions": "Hungria, Finlândia, Estónia, Carélia, Sibéria Ocidental",
        "speakers": "~24,9 milhões de pessoas",
        "parent": "ur",
        "children": ["lang_hu", "lang_fi", "lang_krl", "lang_vot"]
    },
    "lang_hu": {
        "name": "🗣 Húngaro",
        "type": "Língua",
        "regions": "Hungria, Roménia (Transilvânia), Eslováquia, Sérvia",
        "speakers": "~13 milhões de pessoas",
        "status": STATUS["SAFE"],
        "parent": "ur_fu",
        "children": []
    },
    "lang_fi": {
        "name": "🗣 Finlandês",
        "type": "Língua",
        "regions": "Finlândia, Suécia",
        "speakers": "~5,5 milhões de pessoas",
        "status": STATUS["SAFE"],
        "parent": "ur_fu",
        "children": []
    },
    "lang_krl": {
        "name": "🗣 Carélio",
        "type": "Língua",
        "regions": "Rússia (Carélia), Finlândia",
        "speakers": "~25.000–30.000 pessoas",
        "status": STATUS["ENDANGERED"],
        "parent": "ur_fu",
        "children": []
    },
    "lang_vot": {
        "name": "🗣 Vótico",
        "type": "Língua",
        "regions": "Rússia (Oblast de Leninegrado)",
        "speakers": "Menos de 10 pessoas",
        "status": STATUS["CRITICALLY"],
        "parent": "ur_fu",
        "children": []
    },
    "ur_sam": {
        "name": "🌿 Ramo Samoiedo",
        "type": "Ramo",
        "regions": "Extremo Norte da Rússia e Sibéria",
        "speakers": "~25.000 pessoas",
        "parent": "ur",
        "children": ["lang_yrk", "lang_kamas"]
    },
    "lang_yrk": {
        "name": "🗣 Nenets",
        "type": "Língua",
        "regions": "Norte da Rússia (Tundra do Ártico)",
        "speakers": "~22.000 pessoas",
        "status": STATUS["ENDANGERED"],
        "parent": "ur_sam",
        "children": []
    },
    "lang_kamas": {
        "name": "📜 Kamassiano",
        "type": "Língua",
        "regions": "Sul da Sibéria (Montanhas Sayan)",
        "speakers": "0 (a última falante morreu em 1989)",
        "status": STATUS["DEAD"],
        "parent": "ur_sam",
        "children": []
    },

    # ================= 5. FAMÍLIA TÚRQUICA =================
    "turk": {
        "name": "🌐 Família Túrquica",
        "type": "Família linguística",
        "regions": "Anatólia, Ásia Central, Região do Volga, Cáucaso, Sibéria",
        "speakers": "~200 milhões de pessoas",
        "parent": "root",
        "children": ["turk_common", "turk_bulg"]
    },
    "turk_common": {
        "name": "🌿 Ramo Túrquico Comum",
        "type": "Ramo",
        "regions": "Turquia, Azerbaijão, Ásia Central, Volga, Sibéria",
        "speakers": "~198 milhões de pessoas",
        "parent": "turk",
        "children": ["lang_tr", "lang_kk", "lang_tt", "lang_tof"]
    },
    "lang_tr": {
        "name": "🗣 Turco",
        "type": "Língua",
        "regions": "Turquia, Chipre, diásporas na Europa Ocidental",
        "speakers": "~88 milhões de pessoas",
        "status": STATUS["SAFE"],
        "parent": "turk_common",
        "children": []
    },
    "lang_kk": {
        "name": "🗣 Cazaque",
        "type": "Língua",
        "regions": "Cazaquistão, China (Xinjiang), Mongólia, Rússia",
        "speakers": "~16 milhões de pessoas",
        "status": STATUS["SAFE"],
        "parent": "turk_common",
        "children": []
    },
    "lang_tt": {
        "name": "🗣 Tártaro",
        "type": "Língua",
        "regions": "Rússia (Tartaristão, Bascortostão)",
        "speakers": "~5,2 milhões de pessoas",
        "status": STATUS["VULNERABLE"],
        "parent": "turk_common",
        "children": []
    },
    "lang_tof": {
        "name": "🗣 Tofalar",
        "type": "Língua",
        "regions": "Rússia (Oblast de Irkutsk, Sibéria)",
        "speakers": "Menos de 30 pessoas",
        "status": STATUS["CRITICALLY"],
        "parent": "turk_common",
        "children": []
    },
    "turk_bulg": {
        "name": "🌿 Ramo Ogúrico (Búlgaro)",
        "type": "Ramo",
        "regions": "Região do Volga (Chuváchia), historicamente na Grande Bulgária e Cazária",
        "speakers": "~1 milhão de pessoas",
        "parent": "turk",
        "children": ["lang_cv", "lang_zkz"]
    },
    "lang_cv": {
        "name": "🗣 Chuvache",
        "type": "Língua",
        "regions": "Rússia (Chuváchia)",
        "speakers": "~1 milhão de pessoas (única língua viva do ramo ogúrico)",
        "status": STATUS["VULNERABLE"],
        "parent": "turk_bulg",
        "children": []
    },
    "lang_zkz": {
        "name": "📜 Cazar",
        "type": "Língua",
        "regions": "Canato Cazar (Norte do Cáucaso, Baixo Volga)",
        "speakers": "0 (extinta nos séculos X–XI)",
        "status": STATUS["DEAD"],
        "parent": "turk_bulg",
        "children": []
    }
}


def get_breadcrumb(node_id: str) -> str:
    """Constrói o caminho de navegação desde a raiz até ao nó atual."""
    path = []
    current = node_id
    while current:
        node = LANGUAGE_TREE.get(current)
        if not node:
            break
        path.append(node["name"])
        current = node.get("parent")
    return " ➔ ".join(reversed(path))


def format_node_text(node_id: str) -> str:
    """Formata o texto informativo da família, ramo ou língua."""
    node = LANGUAGE_TREE[node_id]
    lines = [
        f"<b>{node['name']}</b>",
        f"<i>Caminho: {get_breadcrumb(node_id)}</i>\n",
        f"📌 <b>Categoria:</b> {node['type']}",
        f"🗺 <b>Territórios de difusão:</b> {node['regions']}",
        f"👥 <b>Número de falantes:</b> {node['speakers']}"
    ]

    if "status" in node:
        lines.append(f"📊 <b>Estado de conservação:</b> {node['status']}")

    if "info" in node:
        lines.append(f"\n💡 <i>{node['info']}</i>")

    if node["children"]:
        lines.append("\n👇 <b>Selecione um nível abaixo para avançar:</b>")

    return "\n".join(lines)


def build_keyboard(node_id: str):
    """Cria o teclado inline para o nó atual da árvore."""
    builder = InlineKeyboardBuilder()
    node = LANGUAGE_TREE[node_id]

    for child_id in node["children"]:
        child = LANGUAGE_TREE[child_id]
        builder.button(text=child["name"], callback_data=f"node:{child_id}")

    builder.adjust(1)

    nav_buttons = []
    if node["parent"]:
        nav_buttons.append(("⬅️ Voltar um nível", f"node:{node['parent']}"))
    if node_id != "root":
        nav_buttons.append(("🏠 Voltar ao início", "node:root"))

    if nav_buttons:
        nav_builder = InlineKeyboardBuilder()
        for text, cb in nav_buttons:
            nav_builder.button(text=text, callback_data=cb)
        nav_builder.adjust(len(nav_buttons))
        builder.attach(nav_builder)

    return builder.as_markup()


dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        text=format_node_text("root"),
        reply_markup=build_keyboard("root")
    )


@dp.callback_query(F.data.startswith("node:"))
async def navigate_tree(callback: CallbackQuery):
    node_id = callback.data.split(":", 1)[1]
    if node_id not in LANGUAGE_TREE:
        await callback.answer("Seção não encontrada", show_alert=True)
        return

    try:
        await callback.message.edit_text(
            text=format_node_text(node_id),
            reply_markup=build_keyboard(node_id)
        )
    except TelegramBadRequest:
        pass
    await callback.answer()


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
