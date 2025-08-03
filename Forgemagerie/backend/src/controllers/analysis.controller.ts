import { Request, Response } from 'express';
import { DofapiService } from '../services/dofapi.service';
import { ForgemageService } from '../services/forge-magic';
import { RunesService } from '../services/runes.service';

export class AnalysisController {
  private dofapiService: DofapiService;
  private forgemageService: ForgemageService;
  private runesService: RunesService;

  constructor() {
    this.dofapiService = new DofapiService();
    this.forgemageService = new ForgemageService();
    this.runesService = new RunesService();
  }

  async analyzeItem(req: Request, res: Response): Promise<void> {
    try {
      const { itemName, targetStats, statsASupprimer = {} } = req.body;

      if (!itemName || !targetStats) {
        res.status(400).json({
          error: 'itemName et targetStats sont requis'
        });
        return;
      }

      const searchResults = await this.dofapiService.searchItem(itemName);
      
      if (searchResults.length === 0) {
        res.status(404).json({
          error: 'Aucun objet trouvé avec ce nom'
        });
        return;
      }

      const dofapiItem = searchResults[0];
      const item = this.dofapiService.convertToDofusItem(dofapiItem);
      
      item.baseStats.prix = await this.dofapiService.getItemPrices(item.id);

      const availableRunes = this.runesService.getAllRunes();

      const analysis = this.forgemageService.analyzeItem(
        item,
        targetStats,
        availableRunes,
        statsASupprimer
      );

      res.json({
        success: true,
        data: analysis
      });

    } catch (error) {
      console.error('Erreur lors de l\'analyse:', error);
      res.status(500).json({
        error: error instanceof Error ? error.message : 'Erreur interne'
      });
    }
  }

  async searchItems(req: Request, res: Response): Promise<void> {
    try {
      const { query } = req.query;

      if (!query || typeof query !== 'string') {
        res.status(400).json({
          error: 'Paramètre de recherche requis'
        });
        return;
      }

      const results = await this.dofapiService.searchItem(query);
      
      const items = results.map(item => ({
        id: item.id,
        name: item.name.fr,
        type: item.type.name.fr,
        level: item.level
      }));

      res.json({
        success: true,
        data: items
      });

    } catch (error) {
      console.error('Erreur lors de la recherche:', error);
      res.status(500).json({
        error: 'Erreur lors de la recherche'
      });
    }
  }

  async getItemDetails(req: Request, res: Response): Promise<void> {
    try {
      const { id } = req.params;
      const itemId = parseInt(id);

      if (isNaN(itemId)) {
        res.status(400).json({
          error: 'ID d\'objet invalide'
        });
        return;
      }

      const dofapiItem = await this.dofapiService.getItemById(itemId);
      
      if (!dofapiItem) {
        res.status(404).json({
          error: 'Objet non trouvé'
        });
        return;
      }

      const item = this.dofapiService.convertToDofusItem(dofapiItem);
      item.baseStats.prix = await this.dofapiService.getItemPrices(item.id);

      res.json({
        success: true,
        data: item
      });

    } catch (error) {
      console.error('Erreur lors de la récupération de l\'objet:', error);
      res.status(500).json({
        error: 'Erreur lors de la récupération de l\'objet'
      });
    }
  }

  async getRunes(req: Request, res: Response): Promise<void> {
    try {
      const { type, effect } = req.query;

      let runes;

      if (type && typeof type === 'string') {
        runes = this.runesService.getRunesByType(type);
      } else if (effect && typeof effect === 'string') {
        runes = this.runesService.getRunesByEffect(effect);
      } else {
        runes = this.runesService.getAllRunes();
      }

      res.json({
        success: true,
        data: runes
      });

    } catch (error) {
      console.error('Erreur lors de la récupération des runes:', error);
      res.status(500).json({
        error: 'Erreur lors de la récupération des runes'
      });
    }
  }

  async calculatePuits(req: Request, res: Response): Promise<void> {
    try {
      const { itemId, targetStats, statsASupprimer = {} } = req.body;

      if (!itemId || !targetStats) {
        res.status(400).json({
          error: 'itemId et targetStats sont requis'
        });
        return;
      }

      const dofapiItem = await this.dofapiService.getItemById(itemId);
      
      if (!dofapiItem) {
        res.status(404).json({
          error: 'Objet non trouvé'
        });
        return;
      }

      const item = this.dofapiService.convertToDofusItem(dofapiItem);

      const puitsUtilise = this.forgemageService.calculPuits(item, targetStats);
      const puitsDisponible = this.forgemageService.calculPuitsDisponible(item, statsASupprimer);

      res.json({
        success: true,
        data: {
          puitsUtilise,
          puitsDisponible,
          puitsRestant: puitsDisponible - puitsUtilise,
          feasible: puitsUtilise <= puitsDisponible
        }
      });

    } catch (error) {
      console.error('Erreur lors du calcul du puits:', error);
      res.status(500).json({
        error: 'Erreur lors du calcul du puits'
      });
    }
  }
}