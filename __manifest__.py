{
    "name": "Hotel Management",
    "icon": "static/description/hotel.png",
    "version": "17.0.1.0.0",
    "category": "Addons",
    "summary": "Hotel Management",
    "description": """Hotel Management""",
    "author": "Naura",
    "company": "PT SOLU FILANTROPI TEKNOLOGI",
    "maintainer": "ERP Team of SOLU FILANTROPI TEKNOLOGI",
    "depends": ["web", "mail", "product"],
    "data": [
        "security/ir.model.access.csv",
        "views/hotel_management_view.xml",
        "views/hotel_rooms_view.xml",
        "views/hotel_reservation_view.xml",
        "views/hotel_report_view.xml",
        "views/hotel_menu.xml",
        ],
    "assets": {
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
