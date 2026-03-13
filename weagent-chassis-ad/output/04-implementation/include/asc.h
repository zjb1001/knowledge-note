/******************************************************************************
 * @file asc.h
 * @brief Air Suspension Control - Interface Definition
 * @version 1.0.0
 * @author WeAgent Multi-Agent System
 * @date 2026-03-13
 * 
 * ASIL Level: B
 ******************************************************************************/

#ifndef ASC_H
#define ASC_H

#include "Std_Types.h"

/*============================================================================*
 * MACRO DEFINITIONS
 *============================================================================*/
#define ASC_CYCLE_TIME_MS               50U
#define ASC_HEIGHT_RANGE                50      /* mm */
#define ASC_HEIGHT_PRECISION            5       /* mm */
#define ASC_ADJUST_SPEED                5       /* mm/s */

/*============================================================================*
 * TYPE DEFINITIONS
 *============================================================================*/
typedef uint8_t Asc_HeightModeType;
#define ASC_HEIGHT_LOW                  0x00U
#define ASC_HEIGHT_NORMAL               0x01U
#define ASC_HEIGHT_HIGH                 0x02U
#define ASC_HEIGHT_WELCOME              0x03U

typedef uint8_t Asc_DampingModeType;
#define ASC_DAMPING_SOFT                0x00U
#define ASC_DAMPING_MEDIUM              0x01U
#define ASC_DAMPING_HARD                0x02U
#define ASC_DAMPING_ADAPTIVE            0x03U

/*============================================================================*
 * GLOBAL FUNCTIONS
 *============================================================================*/
extern void Asc_Init(void);
extern void Asc_MainFunction(void);
extern void Asc_HeightControl(sint16 targetHeight, const void* vehicleState);
extern void Asc_LevelingControl(const void* vehicleState);
extern void Asc_CDCControl(const void* vehicleState);

#endif /* ASC_H */
