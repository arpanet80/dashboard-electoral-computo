import { Controller, Post, Body, Get, HttpException, HttpStatus, Query } from '@nestjs/common';
import { MaletasService } from './maletas.service';

@Controller('api')
export class MaletasController {
  constructor(private readonly maletasService: MaletasService) {}

  @Post('login')
  async login(@Body() credentials: any) {
    try {
      const result = await this.maletasService.login(credentials);
      return result;
    } catch (error) {
      throw new HttpException(
        { error: 'Login failed', message: error.message },
        HttpStatus.UNAUTHORIZED
      );
    }
  }

  @Get('maletas-data')
  async getMaletasData() {
    try {
      const data = await this.maletasService.getMaletasData();
      return data;
    } catch (error) {
      throw new HttpException(
        { error: 'Data fetch failed', message: error.message },
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }

  @Post('manual-login')
  async manualLogin(@Body() credentials: any) {
    try {
      const result = await this.maletasService.manualLogin(credentials);
      return result;
    } catch (error) {
      throw new HttpException(
        { error: 'Manual login failed', message: error.message },
        HttpStatus.UNAUTHORIZED
      );
    }
  }

  @Get('session-status')
  getSessionStatus() {
    return this.maletasService.getSessionStatus();
  }

  @Post('logout')
  logout() {
    return this.maletasService.logout();
  }


  @Get('resumen-maletas')
  async getResumenMaletas() {
    try {
      const data = await this.maletasService.getResumenMaletas();
      return {
        success: true,
        message: 'Resumen de maletas obtenido exitosamente',
        data: data
      };
    } catch (error) {
      throw new HttpException(
        { 
          success: false,
          error: 'RESUMEN_FETCH_FAILED',
          message: error.message 
        },
        HttpStatus.INTERNAL_SERVER_ERROR
      );
    }
  }


  @Get('reporte-monitoreo')
async getReporteMonitoreo(@Query('departamento') departamento?: number) {
  try {
    const idDepartamento = departamento || 5; // Default a Potosí (5)
    const data = await this.maletasService.getReporteMonitoreo(idDepartamento);
    return {
      success: true,
      message: 'Reporte de monitoreo obtenido exitosamente',
      data: data
    };
  } catch (error) {
    throw new HttpException(
      { 
        success: false,
        error: 'MONITOREO_FETCH_FAILED',
        message: error.message 
      },
      HttpStatus.INTERNAL_SERVER_ERROR
    );
  }
}

@Get('resumen-general')
async getResumenGeneral(@Query('departamento') departamento?: number) {
  try {
    const idDepartamento = departamento || 5; // Default a Potosí (5)
    const data = await this.maletasService.getResumenGeneral(idDepartamento);
    return {
      success: true,
      message: 'Resumen general obtenido exitosamente',
      data: data
    };
  } catch (error) {
    throw new HttpException(
      { 
        success: false,
        error: 'RESUMEN_GENERAL_FETCH_FAILED',
        message: error.message 
      },
      HttpStatus.INTERNAL_SERVER_ERROR
    );
  }
}

}