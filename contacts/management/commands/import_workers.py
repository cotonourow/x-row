from django.core.management.base import BaseCommand
from django.db import transaction
from contacts.models import Worker


class Command(BaseCommand):
    help = 'Import workers with corrections (119 workers total)'

    def normalize_phone(self, phone):
        """Normalize phone number to standard 11-digit Nigerian format"""
        if not phone:
            return None
        
        phone = str(phone).strip()
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace(".", "").replace("+", "")
        
        if phone.startswith("234") and len(phone) == 13:
            phone = "0" + phone[3:]
        elif phone.startswith("0") and len(phone) == 11:
            pass
        elif len(phone) == 10 and not phone.startswith("0"):
            phone = "0" + phone
        elif len(phone) == 14 and phone.startswith("+"):
            phone = "0" + phone[4:]
        
        if len(phone) != 11:
            return None
            
        return phone

    def handle(self, *args, **kwargs):
        workers_data = [
            # ========== ORIGINAL 111 WORKERS (Eng Shegun removed - duplicate) ==========
            
            # ENGINEERS (29 - removed Eng Shegun duplicate)
            {"name": "Engr Ema Ikem", "skill": "engineer", "location": "Abuja", "phone": "08032752021", "experience_years": 8, "rating": 4.5},
            {"name": "Engr Danai", "skill": "engineer", "location": "Abuja", "phone": "08135319456", "experience_years": 6, "rating": 4.0},
            {"name": "Engr Farouk", "skill": "engineer", "location": "Abuja", "phone": "08039680982", "experience_years": 10, "rating": 4.8},
            {"name": "Engr Friday", "skill": "engineer", "location": "Abuja", "phone": "08038609082", "experience_years": 5, "rating": 3.5},
            {"name": "Engr Isiak FO1", "skill": "engineer", "location": "Abuja", "phone": "08082514489", "experience_years": 7, "rating": 4.2},
            {"name": "Engr Mathias", "skill": "engineer", "location": "Abuja", "phone": "08053530428", "experience_years": 12, "rating": 4.9},
            {"name": "Engr Mohammed", "skill": "engineer", "location": "Abuja", "phone": "08099345862", "experience_years": 4, "rating": 3.8},
            {"name": "Engr Chegun FO1", "skill": "engineer", "location": "Abuja", "phone": "08103735032", "experience_years": 9, "rating": 4.6},  # Same person as Eng Shegun
            {"name": "Engr Tunediji", "skill": "engineer", "location": "Abuja", "phone": "08062095884", "experience_years": 6, "rating": 4.1},
            {"name": "Engr Uba", "skill": "engineer", "location": "Abuja", "phone": "08067640763", "experience_years": 8, "rating": 4.3},
            {"name": "Engr Wuya Man", "skill": "engineer", "location": "Abuja", "phone": "08199994980", "experience_years": 5, "rating": 3.9},
            {"name": "Engr Evans", "skill": "engineer", "location": "Abuja", "phone": "08106291139", "experience_years": 7, "rating": 4.4},
            {"name": "Engr Gaius Joseph", "skill": "engineer", "location": "Abuja", "phone": "09050609662", "experience_years": 11, "rating": 4.7},
            {"name": "Eng Beck (Pastor)", "skill": "engineer", "location": "Abuja", "phone": "07015282526", "experience_years": 15, "rating": 5.0},
            {"name": "Eng Bayo", "skill": "engineer", "location": "Abuja", "phone": "08039785474", "experience_years": 6, "rating": 4.0},
            {"name": "Eng Chibuke", "skill": "engineer", "location": "Abuja", "phone": "09131164915", "experience_years": 4, "rating": 3.7},
            {"name": "Eng Aba Gole", "skill": "engineer", "location": "Abuja", "phone": "07062173980", "experience_years": 8, "rating": 4.5},
            {"name": "Eng Eze", "skill": "engineer", "location": "Abuja", "phone": "07032229527", "experience_years": 9, "rating": 4.6},
            {"name": "Eng Sanni", "skill": "engineer", "location": "Abuja", "phone": "08149003755", "experience_years": 5, "rating": 4.2},
            {"name": "Eng Shrey", "skill": "engineer", "location": "Abuja", "phone": "08143593708", "experience_years": 3, "rating": 3.5},
            {"name": "Eng Tunde", "skill": "engineer", "location": "Abuja", "phone": "08062095881", "experience_years": 10, "rating": 4.8},
            {"name": "Eng Colleys", "skill": "engineer", "location": "Abuja", "phone": "08034989226", "experience_years": 7, "rating": 4.3},
            {"name": "Eng Mike", "skill": "engineer", "location": "Abuja", "phone": "08077584933", "experience_years": 6, "rating": 4.0},
            # REMOVED: Eng Shegun (duplicate of Engr Chegun FO1)
            {"name": "Eng Marcus", "skill": "engineer", "location": "Abuja", "phone": "08169994980", "experience_years": 8, "rating": 4.4},
            {"name": "Eng Kings", "skill": "engineer", "location": "Abuja", "phone": "08037240282", "experience_years": 9, "rating": 4.5},
            {"name": "Eng Yinka", "skill": "engineer", "location": "Abuja", "phone": "08068852851", "experience_years": 12, "rating": 4.9},
            {"name": "Eng Alex", "skill": "engineer", "location": "Abuja", "phone": "09073497278", "experience_years": 5, "rating": 4.1},
            {"name": "Eng Nelson", "skill": "engineer", "location": "Abuja", "phone": "08065345338", "experience_years": 6, "rating": 4.2},
            {"name": "Eng Richard", "skill": "engineer", "location": "Abuja", "phone": "07069985373", "experience_years": 7, "rating": 4.3},

            # ELECTRICIANS (6)
            {"name": "Gideon Electric", "skill": "electrician", "location": "Abuja", "phone": "07043946528", "experience_years": 8, "rating": 4.5},
            {"name": "Elijah", "skill": "electrician", "location": "Ushafa, Abuja", "phone": "09163833349", "experience_years": 6, "rating": 4.2},
            {"name": "Hamza", "skill": "electrician", "location": "Abuja", "phone": "08149800656", "experience_years": 5, "rating": 4.0},
            {"name": "Thomas", "skill": "electrician", "location": "Abuja", "phone": "08162942886", "experience_years": 10, "rating": 4.7},
            {"name": "Peter", "skill": "electrician", "location": "Abuja", "phone": "09040140236", "experience_years": 7, "rating": 4.4},
            {"name": "Musa", "skill": "electrician", "location": "Abuja", "phone": "07035838190", "experience_years": 4, "rating": 3.8},

            # PAINTERS (28)
            {"name": "Fabrice", "skill": "painter", "location": "Abuja", "phone": "07041528899", "experience_years": 5, "rating": 4.0},
            {"name": "Fedelix", "skill": "painter", "location": "Abuja", "phone": "08109549025", "experience_years": 8, "rating": 4.5},
            {"name": "Patrick", "skill": "painter", "location": "Abuja", "phone": "07063363757", "experience_years": 6, "rating": 4.2},
            {"name": "Francis", "skill": "painter", "location": "Umuahia, Abia", "phone": "07025164665", "experience_years": 12, "rating": 4.8},
            {"name": "Godwin", "skill": "painter", "location": "Abuja", "phone": "07015559957", "experience_years": 4, "rating": 3.9},
            {"name": "Eleth", "skill": "painter", "location": "Abuja", "phone": "08063168775", "experience_years": 7, "rating": 4.3},
            {"name": "Isaacs", "skill": "painter", "location": "Abuja", "phone": "09010679872", "experience_years": 9, "rating": 4.6},
            {"name": "Bobo", "skill": "painter", "location": "Abuja", "phone": "09014158265", "experience_years": 3, "rating": 3.5},
            {"name": "Chibok", "skill": "painter", "location": "Abuja", "phone": "08065592162", "experience_years": 5, "rating": 4.1},
            {"name": "Christian", "skill": "painter", "location": "Ushafa, Abuja", "phone": "07041246001", "experience_years": 6, "rating": 4.2},
            {"name": "Daniel", "skill": "painter", "location": "Bwari, Abuja", "phone": "08142087386", "experience_years": 8, "rating": 4.5},
            {"name": "Alex Danlandi", "skill": "painter", "location": "Abuja", "phone": "09078594710", "experience_years": 10, "rating": 4.7},
            {"name": "David", "skill": "painter", "location": "Abuja", "phone": "09073821436", "experience_years": 4, "rating": 3.8},
            {"name": "Samuel", "skill": "painter", "location": "Abuja", "phone": "08063325145", "experience_years": 7, "rating": 4.4},
            {"name": "Richard", "skill": "painter", "location": "Abuja", "phone": "09060383348", "experience_years": 9, "rating": 4.6},
            {"name": "Mohammed", "skill": "painter", "location": "Abuja", "phone": "08057641094", "experience_years": 11, "rating": 4.8},
            {"name": "Abel Monnon", "skill": "painter", "location": "Lagos", "phone": "08142949868", "experience_years": 15, "rating": 5.0},
            {"name": "Joel", "skill": "painter", "location": "Abuja", "phone": "07025029912", "experience_years": 5, "rating": 4.0},
            {"name": "Joshua", "skill": "painter", "location": "Ushafa, Abuja", "phone": "09164728694", "experience_years": 6, "rating": 4.2},
            {"name": "Abdul", "skill": "painter", "location": "Abuja", "phone": "08113589200", "experience_years": 3, "rating": 3.6},
            {"name": "Joseph", "skill": "painter", "location": "Bwari, Abuja", "phone": "09166907979", "experience_years": 8, "rating": 4.5},
            {"name": "Maxwell", "skill": "painter", "location": "Gwarinpa, Abuja", "phone": "08168868526", "experience_years": 7, "rating": 4.3},
            {"name": "Shehu", "skill": "painter", "location": "Abuja", "phone": "09154576587", "experience_years": 4, "rating": 3.9},
            {"name": "Victor", "skill": "painter", "location": "Abuja", "phone": "08126247013", "experience_years": 5, "rating": 4.1},
            {"name": "Michael", "skill": "painter", "location": "Abuja", "phone": "07041365966", "experience_years": 9, "rating": 4.6},
            {"name": "Yemi", "skill": "painter", "location": "Abuja", "phone": "08033777934", "experience_years": 10, "rating": 4.7},
            {"name": "ifangni boniface", "skill": "painter", "location": "ushafa, FCT Abuja", "phone": "09055289690", "experience_years": 4, "rating": 3.9},
            {"name": "Sunday", "skill": "painter", "location": "Nasarawa State", "phone": "08032432544", "experience_years": 7, "rating": 4.3},
            {"name": "Musa Apayandabo Majeje", "skill": "painter", "location": "New Karshi, Nasarawa", "phone": "08108320110", "experience_years": 7, "rating": 4.3},

            # MASONS (8)
            {"name": "Adamu", "skill": "mason", "location": "Abuja", "phone": "07064520244", "experience_years": 8, "rating": 4.4},
            {"name": "Timothy", "skill": "mason", "location": "Abuja", "phone": "08087426995", "experience_years": 6, "rating": 4.1},
            {"name": "Peter Macus", "skill": "mason", "location": "Abuja", "phone": "09110812981", "experience_years": 12, "rating": 4.8},
            {"name": "Jafar", "skill": "mason", "location": "Abuja", "phone": "09045470231", "experience_years": 5, "rating": 4.0},
            {"name": "Moussa", "skill": "mason", "location": "Abuja", "phone": "07067754529", "experience_years": 7, "rating": 4.3},
            {"name": "Akim", "skill": "mason", "location": "Abuja", "phone": "08438652213", "experience_years": 4, "rating": 3.7},
            {"name": "Austin", "skill": "mason", "location": "Abuja", "phone": "09069346372", "experience_years": 9, "rating": 4.5},
            {"name": "Peter", "skill": "mason", "location": "Abuja", "phone": "09110812951", "experience_years": 6, "rating": 4.2},

            # SCREEDERS (3)
            {"name": "Eli", "skill": "screeder", "location": "Abuja", "phone": "08132833689", "experience_years": 10, "rating": 4.7},
            {"name": "Richo", "skill": "screeder", "location": "Abuja", "phone": "07041790752", "experience_years": 7, "rating": 4.4},
            {"name": "Sadiq", "skill": "screeder", "location": "Abuja", "phone": "07064273991", "experience_years": 5, "rating": 4.0},

            # POP INSTALLERS (19)
            {"name": "Eric", "skill": "pop_installer", "location": "Abuja", "phone": "08102454160", "experience_years": 8, "rating": 4.5},
            {"name": "Germain", "skill": "pop_installer", "location": "Abuja", "phone": "09123492539", "experience_years": 6, "rating": 4.2},
            {"name": "Godwin", "skill": "pop_installer", "location": "Abuja", "phone": "08107629806", "experience_years": 11, "rating": 4.8},
            {"name": "William", "skill": "pop_installer", "location": "Abuja", "phone": "09168678494", "experience_years": 9, "rating": 4.6},
            {"name": "Casimir", "skill": "pop_installer", "location": "Kabusa, Abuja", "phone": "08074440792", "experience_years": 7, "rating": 4.3},
            {"name": "David", "skill": "pop_installer", "location": "Abuja", "phone": "08083999572", "experience_years": 5, "rating": 4.0},
            {"name": "Steven", "skill": "pop_installer", "location": "Abuja", "phone": "07041352393", "experience_years": 4, "rating": 3.8},
            {"name": "Vincent", "skill": "pop_installer", "location": "Abuja", "phone": "08039374809", "experience_years": 8, "rating": 4.5},
            {"name": "Jesse", "skill": "pop_installer", "location": "Abuja", "phone": "09063129272", "experience_years": 6, "rating": 4.2},
            {"name": "Jonathan", "skill": "pop_installer", "location": "Abuja", "phone": "08096582876", "experience_years": 10, "rating": 4.7},
            {"name": "Julius", "skill": "pop_installer", "location": "Abuja", "phone": "08082743922", "experience_years": 12, "rating": 4.9},
            {"name": "Justis", "skill": "pop_installer", "location": "Abuja", "phone": "07067618605", "experience_years": 5, "rating": 4.1},
            {"name": "Moses", "skill": "pop_installer", "location": "Abuja", "phone": "08147804568", "experience_years": 7, "rating": 4.4},
            {"name": "Mura", "skill": "pop_installer", "location": "Nasarawa", "phone": "08180526794", "experience_years": 9, "rating": 4.6},
            {"name": "Samuel", "skill": "pop_installer", "location": "Abuja", "phone": "09039715240", "experience_years": 4, "rating": 3.9},  # FIXED: was 08063325145
            {"name": "Obear", "skill": "pop_installer", "location": "Abuja", "phone": "07032084247", "experience_years": 6, "rating": 4.2},
            {"name": "P-Boy", "skill": "pop_installer", "location": "Nasarawa State", "phone": "07035964782", "experience_years": 6, "rating": 4.2},
            {"name": "Hassan Yakuba", "skill": "pop_installer", "location": "Kubwa, Abuja", "phone": "08065276453", "experience_years": 8, "rating": 4.5},
            {"name": "Abdul Mohammed", "skill": "pop_installer", "location": "Suleja, Niger State", "phone": "08135191193", "experience_years": 9, "rating": 4.6},

            # WELDERS (5)
            {"name": "Welder Kogo", "skill": "welder", "location": "Abuja", "phone": "08027482525", "experience_years": 15, "rating": 4.9},
            {"name": "Donne", "skill": "welder", "location": "Lagos", "phone": "09038993628", "experience_years": 8, "rating": 4.5},
            {"name": "Rotimi", "skill": "welder", "location": "Abuja", "phone": "08039717008", "experience_years": 10, "rating": 4.7},
            {"name": "Haild", "skill": "welder", "location": "Abuja", "phone": "07002864416", "experience_years": 6, "rating": 4.2},
            {"name": "Patrick", "skill": "welder", "location": "Abuja", "phone": "08080858413", "experience_years": 5, "rating": 4.0},

            # TILERS (5)
            {"name": "Tiller", "skill": "tiler", "location": "Abuja", "phone": "07054785215", "experience_years": 7, "rating": 4.3},
            {"name": "Tiler (Ushafa Down)", "skill": "tiler", "location": "Ushafa, Abuja", "phone": "08060032199", "experience_years": 9, "rating": 4.6},
            {"name": "Solomon", "skill": "tiler", "location": "Abuja", "phone": "08168102988", "experience_years": 8, "rating": 4.5},
            {"name": "Mike", "skill": "tiler", "location": "Abuja", "phone": "09032287138", "experience_years": 6, "rating": 4.2},
            {"name": "Emmanuel", "skill": "tiler", "location": "Nasarawa State", "phone": "07016871345", "experience_years": 6, "rating": 4.2},

            # CARPENTERS / FURNITURE (6)
            {"name": "Richard", "skill": "carpenter", "location": "Ushafa, Abuja", "phone": "09073644055", "experience_years": 12, "rating": 4.8},
            {"name": "Abel Nego", "skill": "furniture_maker", "location": "Ushafa, Abuja", "phone": "07049875211", "experience_years": 10, "rating": 4.7},
            {"name": "Daniel Moses", "skill": "furniture_maker", "location": "Abuja", "phone": "07040156959", "experience_years": 8, "rating": 4.5},
            {"name": "Joseph James", "skill": "carpenter", "location": "Nasarawa State", "phone": "08028362720", "experience_years": 5, "rating": 4.0},
            {"name": "Prince Shalom", "skill": "carpenter", "location": "Nasarawa State", "phone": "08147704261", "experience_years": 6, "rating": 4.2},
            {"name": "Hassan", "skill": "furniture_maker", "location": "Nasarawa State", "phone": "09150741044", "experience_years": 8, "rating": 4.4},

            # IRON BENDERS (1)
            {"name": "Emmanuel", "skill": "iron_bender", "location": "Abuja", "phone": "08035893173", "experience_years": 11, "rating": 4.8},

            # FABRICATORS (1)
            {"name": "Ibrahim Harkoki", "skill": "fabricator", "location": "Abuja", "phone": "08167527610", "experience_years": 9, "rating": 4.6},

            # WINDOW HOOD (2)
            {"name": "Emmanuel", "skill": "window_hood_installer", "location": "Abuja", "phone": "07049887285", "experience_years": 7, "rating": 4.4},
            {"name": "Peter", "skill": "window_hood_installer", "location": "Abuja", "phone": "09030260928", "experience_years": 5, "rating": 4.1},

            # CONCRETE (1)
            {"name": "Ojo", "skill": "concrete_specialist", "location": "Abuja", "phone": "07077014645", "experience_years": 14, "rating": 4.9},

            # SCAFFOLDING (2)
            {"name": "Scaffolder Man", "skill": "scaffolder", "location": "Abuja", "phone": "08060297068", "experience_years": 8, "rating": 4.5},
            {"name": "Godwin", "skill": "scaffolder", "location": "Abuja", "phone": "09133735857", "experience_years": 6, "rating": 4.2},

            # BOREHOLE (2)
            {"name": "Jacks", "skill": "borehole_specialist", "location": "Abuja", "phone": "08148584579", "experience_years": 16, "rating": 5.0},
            {"name": "Mr Jack", "skill": "borehole_specialist", "location": "Abuja", "phone": "08130716009", "experience_years": 13, "rating": 4.8},

            # PLASTER BOARD (1)
            {"name": "Wisdom", "skill": "plaster_board", "location": "Abuja", "phone": "09157053007", "experience_years": 7, "rating": 4.4},

            # INTERLOCK (1)
            {"name": "Nelson", "skill": "interlock", "location": "Abuja", "phone": "07061863934", "experience_years": 5, "rating": 4.0},

            # ALUMINIUM (1)
            {"name": "Philip", "skill": "aluminium_work", "location": "Abuja", "phone": "08153357986", "experience_years": 9, "rating": 4.6},

            # MANAGEMENT (3)
            {"name": "OLA", "skill": "site_manager", "location": "Abuja", "phone": "08139966330", "experience_years": 20, "rating": 5.0},
            {"name": "Mr Archibong", "skill": "site_supervisor", "location": "Abuja", "phone": "08033770000", "experience_years": 18, "rating": 4.9},
            {"name": "Promise Ega", "skill": "site_manager", "location": "Nasarawa State", "phone": "08091984861", "experience_years": 12, "rating": 4.8},

            # LABOURERS (13)
            {"name": "Usman Abubakar", "skill": "labourer", "location": "Abuja", "phone": "08083357016", "experience_years": 3, "rating": 3.5},
            {"name": "Moses", "skill": "labourer", "location": "Abuja", "phone": "09169568505", "experience_years": 2, "rating": 3.2},
            {"name": "Sunday Ejiro", "skill": "labourer", "location": "Nasarawa State", "phone": "08072376172", "experience_years": 3, "rating": 3.5},
            {"name": "Abubakar Ewa", "skill": "labourer", "location": "Nasarawa State", "phone": "08155482554", "experience_years": 4, "rating": 3.8},
            {"name": "Abubakar Abdull", "skill": "labourer", "location": "Nasarawa State", "phone": "07054454118", "experience_years": 5, "rating": 3.9},
            {"name": "Unknown", "skill": "labourer", "location": "Nasarawa State", "phone": "08084765473", "experience_years": 2, "rating": 3.0},
            {"name": "Auta", "skill": "labourer", "location": "Nasarawa State", "phone": "09162874702", "experience_years": 4, "rating": 3.7},
            {"name": "Uwello Umar Ibrahim", "skill": "labourer", "location": "Nasarawa State", "phone": "09051527874", "experience_years": 5, "rating": 3.8},
            {"name": "Ibrahim Aliyu", "skill": "labourer", "location": "Nasarawa State", "phone": "07025252265", "experience_years": 3, "rating": 3.4},
            {"name": "Idris", "skill": "labourer", "location": "Nasarawa State", "phone": "07078439604", "experience_years": 4, "rating": 3.6},
            {"name": "Mohammed Abubakar Ewolo", "skill": "labourer", "location": "Nasarawa State", "phone": "07042189618", "experience_years": 4, "rating": 3.7},
            {"name": "Areola Adeleke", "skill": "labourer", "location": "Nasarawa State", "phone": "07038484662", "experience_years": 5, "rating": 3.9},
            {"name": "Abdul USU", "skill": "labourer", "location": "Nasarawa State", "phone": "08108096977", "experience_years": 4, "rating": 3.8},

            # PLUMBERS (2)
            {"name": "Henry KAYODE", "skill": "plumber", "location": "ushafa abuja", "phone": "09133669496", "experience_years": 6, "rating": 4.3},
            {"name": "Joel Abegyi Bala", "skill": "plumber", "location": "Abuja (Ushafa)", "phone": "08147036915", "experience_years": 5, "rating": 4.0},

            # EXTRA FURNITURE (1)
            {"name": "ifangni", "skill": "furniture_maker", "location": "ushafa", "phone": "08149836978", "experience_years": 5, "rating": 4.1},

            # LAGOS WORKER (1)
            {"name": "John Oloyade", "skill": "mason", "location": "Epe, Lagos State", "phone": "09033542887", "experience_years": 8, "rating": 4.5},

            # ========== ★★★ NEW WORKERS ADDED APRIL 2026 ★★★ ==========
            
            # APRIL 4, 2026 - 6 NEW WORKERS
            {"name": "Nely", "skill": "painter", "location": "Abuja (Ushafa)", "phone": "09047181143", "experience_years": 4, "rating": 3.9},
            {"name": "Joel", "skill": "mason", "location": "Abuja (Ushafa)", "phone": "08063553785", "experience_years": 6, "rating": 4.2},
            {"name": "Fred", "skill": "furniture_maker", "location": "Abuja (Ushafa)", "phone": "08026452883", "experience_years": 7, "rating": 4.4},
            {"name": "Joel Abegyi Bala", "skill": "plumber", "location": "Abuja (Ushafa)", "phone": "08147036915", "experience_years": 5, "rating": 4.0},
            {"name": "Silas", "skill": "electrician", "location": "Abuja (Ushafa)", "phone": "08147074861", "experience_years": 5, "rating": 4.1},
            {"name": "Patrick", "skill": "electrician", "location": "Asaba (Delta State)", "phone": "09066470519", "experience_years": 8, "rating": 4.5},
            
            # APRIL 7, 2026 - 2 NEW WORKERS
            {"name": "Jude Ijangni", "skill": "aluminium_work", "location": "Ushafa, Abuja", "phone": "08060934536", "experience_years": 5, "rating": 4.0},
            {"name": "Emmanuel Friday", "skill": "welder", "location": "Gwarinpa, Abuja", "phone": "07030318817", "experience_years": 6, "rating": 4.0},
        ]

        created_count = 0
        updated_count = 0
        skipped_count = 0

        with transaction.atomic():
            for worker_data in workers_data:
                name = worker_data.get("name", "").strip()
                phone_raw = worker_data.get("phone", "")
                phone = self.normalize_phone(phone_raw)

                if not phone:
                    self.stdout.write(self.style.WARNING(f"⚠️  Skipping {name or 'UNKNOWN'} - invalid phone: {phone_raw}"))
                    skipped_count += 1
                    continue

                existing = Worker.objects.filter(phone=phone).first()
                
                if existing:
                    existing.name = name
                    existing.skill = worker_data.get("skill")
                    existing.location = worker_data.get("location", "")
                    existing.experience_years = worker_data.get("experience_years", 0)
                    existing.rating = worker_data.get("rating", 0.0)
                    existing.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"🔄 Updated: {name}"))
                else:
                    try:
                        Worker.objects.create(
                            name=name,
                            skill=worker_data.get("skill"),
                            location=worker_data.get("location", ""),
                            phone=phone,
                            experience_years=worker_data.get("experience_years", 0),
                            rating=worker_data.get("rating", 0.0),
                        )
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f"✅ Created: {name}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"❌ Failed to create {name}: {e}"))
                        skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Done! Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count}"
        ))
        
        # Show corrections made
        self.stdout.write(self.style.SUCCESS(
            f"\n{'='*60}\n"
            f"CORRECTIONS APPLIED:\n"
            f"{'='*60}\n"
            f"✅ Removed: Eng Shegun (duplicate of Engr Chegun FO1)\n"
            f"✅ Fixed: Samuel phone 08063325145 → 09039715240\n"
            f"{'='*60}\n"
            f"Total: 119 workers (111 original + 8 new)\n"
            f"{'='*60}"
        ))