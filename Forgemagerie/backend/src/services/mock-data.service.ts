import { DofusItem } from '../types';

export class MockDataService {
  static getRetroItems(): DofusItem[] {
    return [
      // Items iconiques du serveur Retro
      {
        id: 101,
        name: "Gelano",
        type: "Anneau",
        level: 60,
        baseStats: {
          vitalite: 81,
          force: 16,
          intelligence: 16,
          chance: 16,
          agilite: 16,
          resistance_neutre: 6
        },
        maxStats: {
          vitalite: 121,
          force: 26,
          intelligence: 26,
          chance: 26,
          agilite: 26,
          resistance_neutre: 16
        },
        weight: 450,
        puits: 90
      },
      {
        id: 102,
        name: "Anneau des Dragoeufs",
        type: "Anneau",
        level: 80,
        baseStats: {
          vitalite: 101,
          sagesse: 21,
          force: 21,
          intelligence: 21,
          chance: 21,
          agilite: 21
        },
        maxStats: {
          vitalite: 151,
          sagesse: 31,
          force: 31,
          intelligence: 31,
          chance: 31,
          agilite: 31
        },
        weight: 600,
        puits: 120
      },
      {
        id: 103,
        name: "Bottes du Bouftou Royal",
        type: "Bottes",
        level: 100,
        baseStats: {
          vitalite: 201,
          force: 31,
          pm: 1,
          resistance_terre: 16,
          resistance_feu: 16
        },
        maxStats: {
          vitalite: 301,
          force: 51,
          pm: 1,
          resistance_terre: 26,
          resistance_feu: 26
        },
        weight: 800,
        puits: 160
      },
      {
        id: 104,
        name: "Cape Bourbisk",
        type: "Cape",
        level: 120,
        baseStats: {
          vitalite: 251,
          intelligence: 36,
          chance: 36,
          puissance: 21,
          soins: 11
        },
        maxStats: {
          vitalite: 351,
          intelligence: 56,
          chance: 56,
          puissance: 31,
          soins: 21
        },
        weight: 950,
        puits: 190
      },
      {
        id: 105,
        name: "Amulette du Minotot",
        type: "Amulette",
        level: 80,
        baseStats: {
          vitalite: 151,
          force: 26,
          agilite: 26,
          pa: 1,
          tacle: 16
        },
        maxStats: {
          vitalite: 201,
          force: 41,
          agilite: 41,
          pa: 1,
          tacle: 26
        },
        weight: 750,
        puits: 150
      },
      {
        id: 106,
        name: "Ceinture du Blop Royal",
        type: "Ceinture",
        level: 110,
        baseStats: {
          vitalite: 181,
          sagesse: 31,
          puissance: 16,
          resistance_neutre: 11,
          esquive_pm: 6
        },
        maxStats: {
          vitalite: 281,
          sagesse: 51,
          puissance: 26,
          resistance_neutre: 21,
          esquive_pm: 16
        },
        weight: 700,
        puits: 140
      },
      {
        id: 107,
        name: "Coiffe Lynx",
        type: "Coiffe",
        level: 90,
        baseStats: {
          vitalite: 121,
          agilite: 41,
          coup_critique: 9,
          fuite: 21,
          portee: 1
        },
        maxStats: {
          vitalite: 181,
          agilite: 61,
          coup_critique: 16,
          fuite: 36,
          portee: 1
        },
        weight: 850,
        puits: 170
      },
      {
        id: 108,
        name: "Dague du Crâne",
        type: "Dague",
        level: 70,
        baseStats: {
          force: 26,
          agilite: 26,
          puissance: 16,
          coup_critique: 6,
          pa: 1
        },
        maxStats: {
          force: 41,
          agilite: 41,
          puissance: 26,
          coup_critique: 16,
          pa: 1
        },
        weight: 600,
        puits: 120
      },
      {
        id: 109,
        name: "Bâton de Meriana",
        type: "Bâton",
        level: 85,
        baseStats: {
          intelligence: 36,
          sagesse: 21,
          puissance: 21,
          soins: 11,
          pm: 1
        },
        maxStats: {
          intelligence: 56,
          sagesse: 36,
          puissance: 31,
          soins: 21,
          pm: 1
        },
        weight: 750,
        puits: 150
      },
      {
        id: 110,
        name: "Bouclier du Minotot",
        type: "Bouclier",
        level: 75,
        baseStats: {
          vitalite: 126,
          force: 21,
          resistance_neutre: 11,
          resistance_terre: 11,
          tacle: 16
        },
        maxStats: {
          vitalite: 186,
          force: 36,
          resistance_neutre: 21,
          resistance_terre: 21,
          tacle: 26
        },
        weight: 650,
        puits: 130
      }
    ];
  }

  static getMockItems(): DofusItem[] {
    return [
      {
        id: 1,
        name: "Gelano",
        type: "Anneau",
        level: 60,
        baseStats: {
          vitalite: 80,
          force: 15,
          intelligence: 15,
          chance: 15,
          agilite: 15,
          resistance_neutre: 5
        },
        maxStats: {
          vitalite: 120,
          force: 25,
          intelligence: 25,
          chance: 25,
          agilite: 25,
          resistance_neutre: 15
        },
        weight: 450,
        puits: 90
      },
      {
        id: 2,
        name: "Anneau Royal Gelano",
        type: "Anneau",
        level: 185,
        baseStats: {
          vitalite: 350,
          force: 40,
          intelligence: 40,
          chance: 40,
          agilite: 40,
          puissance: 25,
          dommages: 15
        },
        maxStats: {
          vitalite: 450,
          force: 60,
          intelligence: 60,
          chance: 60,
          agilite: 60,
          puissance: 35,
          dommages: 25
        },
        weight: 1200,
        puits: 240
      },
      {
        id: 3,
        name: "Bottes du Bouftou Royal",
        type: "Bottes",
        level: 100,
        baseStats: {
          vitalite: 200,
          force: 30,
          pm: 1,
          resistance_terre: 15,
          resistance_feu: 15
        },
        maxStats: {
          vitalite: 300,
          force: 50,
          pm: 1,
          resistance_terre: 25,
          resistance_feu: 25
        },
        weight: 800,
        puits: 160
      },
      {
        id: 4,
        name: "Cape Bourbisk",
        type: "Cape",
        level: 120,
        baseStats: {
          vitalite: 250,
          intelligence: 35,
          chance: 35,
          puissance: 20,
          soins: 10
        },
        maxStats: {
          vitalite: 350,
          intelligence: 55,
          chance: 55,
          puissance: 30,
          soins: 20
        },
        weight: 950,
        puits: 190
      },
      {
        id: 5,
        name: "Amulette du Minotot",
        type: "Amulette",
        level: 80,
        baseStats: {
          vitalite: 150,
          force: 25,
          agilite: 25,
          pa: 1,
          tacle: 15
        },
        maxStats: {
          vitalite: 200,
          force: 40,
          agilite: 40,
          pa: 1,
          tacle: 25
        },
        weight: 750,
        puits: 150
      },
      {
        id: 6,
        name: "Ceinture du Blop Royal",
        type: "Ceinture",
        level: 110,
        baseStats: {
          vitalite: 180,
          sagesse: 30,
          puissance: 15,
          resistance_neutre: 10,
          esquive_pm: 5
        },
        maxStats: {
          vitalite: 280,
          sagesse: 50,
          puissance: 25,
          resistance_neutre: 20,
          esquive_pm: 15
        },
        weight: 700,
        puits: 140
      },
      {
        id: 7,
        name: "Coiffe Lynx",
        type: "Coiffe",
        level: 90,
        baseStats: {
          vitalite: 120,
          agilite: 40,
          coup_critique: 8,
          fuite: 20,
          portee: 1
        },
        maxStats: {
          vitalite: 180,
          agilite: 60,
          coup_critique: 15,
          fuite: 35,
          portee: 1
        },
        weight: 850,
        puits: 170
      },
      {
        id: 8,
        name: "Épée Feudala",
        type: "Épée",
        level: 150,
        baseStats: {
          force: 45,
          intelligence: 20,
          puissance: 30,
          dommages: 20,
          coup_critique: 10
        },
        maxStats: {
          force: 65,
          intelligence: 35,
          puissance: 45,
          dommages: 35,
          coup_critique: 20
        },
        weight: 1100,
        puits: 220
      }
    ];
  }

  static getMockItemByName(name: string): DofusItem | null {
    const items = this.getMockItems();
    return items.find(item => 
      item.name.toLowerCase().includes(name.toLowerCase())
    ) || null;
  }

  static searchMockItems(query: string): DofusItem[] {
    const items = this.getMockItems();
    return items.filter(item => 
      item.name.toLowerCase().includes(query.toLowerCase()) ||
      item.type.toLowerCase().includes(query.toLowerCase())
    ).slice(0, 10);
  }
}