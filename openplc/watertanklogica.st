PROGRAM program0
  VAR
    LowLevelSensor AT %IX0.5 : BOOL;
    ZoneAButton AT %IX0.6 : BOOL;
    ZoneBButton AT %IX0.7 : BOOL;
    ZoneCButton AT %IX0.8 : BOOL;
    ZoneDButton AT %IX0.9 : BOOL;
    HighLevelSensor AT %IX0.4 : BOOL;
    OverFlowSensor AT %IX0.3 : BOOL;
    Pump AT %QX0.1 : BOOL;
    Alarm AT %QX0.0 : BOOL;
    StartButton AT %IX0.0 : BOOL;
    StopButton AT %IX0.1 : BOOL;
    DrainButton AT %IX0.2 : BOOL;
    DrainValve AT %QX0.3 : BOOL;
    ValveZoneA AT %QX0.4 : BOOL;
    ValveZoneB AT %QX0.5 : BOOL;
    ValveZoneC AT %QX0.6 : BOOL;
    ValveZoneD AT %QX0.7 : BOOL;
  END_VAR

  Pump := NOT(StopButton) AND (Pump OR LowLevelSensor AND StartButton);
  Alarm := OverFlowSensor;
  DrainValve := DrainButton AND NOT(LowLevelSensor);
  ValveZoneA := ZoneAButton;
  ValveZoneB := ZoneBButton;
  ValveZoneC := ZoneCButton;
  ValveZoneD := ZoneDButton;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : program0;
  END_RESOURCE
END_CONFIGURATION

(*DBG:char md5[] = "4cbc7fe8a4ee6f650d69e24986a67c28";*)
(*DBG:/**)
(*DBG: * This file is part of OpenPLC Runtime*)
(*DBG: **)
(*DBG: * Copyright (C) 2023 Autonomy, GP Orcullo*)
(*DBG: * Based on the work by GP Orcullo on Beremiz for uC*)
(*DBG: **)
(*DBG: * This program is free software; you can redistribute it and/or*)
(*DBG: * modify it under the terms of the GNU General Public License*)
(*DBG: * as published by the Free Software Foundation; either version 2*)
(*DBG: * of the License, or (at your option) any later version.*)
(*DBG: **)
(*DBG: * This program is distributed in the hope that it will be useful,*)
(*DBG: * but WITHOUT ANY WARRANTY; without even the implied warranty of*)
(*DBG: * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the*)
(*DBG: * GNU General Public License for more details.*)
(*DBG: **)
(*DBG: * You should have received a copy of the GNU General Public License*)
(*DBG: * along with this program; If not, see <http://www.gnu.org/licenses/>.*)
(*DBG: **)
(*DBG: */*)
(*DBG:*)
(*DBG:#include <stdbool.h>*)
(*DBG:*)
(*DBG:#include "iec_types_all.h"*)
(*DBG:#include "POUS.h"*)
(*DBG:*)
(*DBG:#define SAME_ENDIANNESS      0*)
(*DBG:#define REVERSE_ENDIANNESS   1*)
(*DBG:*)
(*DBG:uint8_t endianness;*)
(*DBG:*)
(*DBG:*)
(*DBG:extern PROGRAM0 RES0__INSTANCE0;*)
(*DBG:*)
(*DBG:static const struct {*)
(*DBG:    void *ptr;*)
(*DBG:    __IEC_types_enum type;*)
(*DBG:} debug_vars[] = {*)
(*DBG:    {&(RES0__INSTANCE0.LOWLEVELSENSOR), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.ZONEABUTTON), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.ZONEBBUTTON), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.ZONECBUTTON), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.ZONEDBUTTON), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.HIGHLEVELSENSOR), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.OVERFLOWSENSOR), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.PUMP), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.ALARM), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.STARTBUTTON), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.STOPBUTTON), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DRAINBUTTON), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.DRAINVALVE), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.VALVEZONEA), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.VALVEZONEB), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.VALVEZONEC), BOOL_ENUM},*)
(*DBG:    {&(RES0__INSTANCE0.VALVEZONED), BOOL_ENUM},*)
(*DBG:};*)
(*DBG:*)
(*DBG:#define VAR_COUNT               17*)
(*DBG:*)
(*DBG:uint16_t get_var_count(void)*)
(*DBG:{*)
(*DBG:    return VAR_COUNT;*)
(*DBG:}*)
(*DBG:*)
(*DBG:size_t get_var_size(size_t idx)*)
(*DBG:{*)
(*DBG:    if (idx >= VAR_COUNT)*)
(*DBG:    {*)
(*DBG:        return 0;*)
(*DBG:    }*)
(*DBG:    switch (debug_vars[idx].type) {*)
(*DBG:    case BOOL_ENUM:*)
(*DBG:        return sizeof(BOOL);*)
(*DBG:    default:*)
(*DBG:        return 0;*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void *get_var_addr(size_t idx)*)
(*DBG:{*)
(*DBG:    void *ptr = debug_vars[idx].ptr;*)
(*DBG:*)
(*DBG:    switch (debug_vars[idx].type) {*)
(*DBG:    case BOOL_ENUM:*)
(*DBG:        return (void *)&((__IEC_BOOL_t *) ptr)->value;*)
(*DBG:    default:*)
(*DBG:        return 0;*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void force_var(size_t idx, bool forced, void *val)*)
(*DBG:{*)
(*DBG:    void *ptr = debug_vars[idx].ptr;*)
(*DBG:*)
(*DBG:    if (forced) {*)
(*DBG:        size_t var_size = get_var_size(idx);*)
(*DBG:        switch (debug_vars[idx].type) {*)
(*DBG:        case BOOL_ENUM: {*)
(*DBG:            memcpy(&((__IEC_BOOL_t *) ptr)->value, val, var_size);*)
(*DBG:            //((__IEC_BOOL_t *) ptr)->value = *((BOOL *) val);*)
(*DBG:            ((__IEC_BOOL_t *) ptr)->flags |= __IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:        default:*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:    } else {*)
(*DBG:        switch (debug_vars[idx].type) {*)
(*DBG:        case BOOL_ENUM:*)
(*DBG:            ((__IEC_BOOL_t *) ptr)->flags &= ~__IEC_FORCE_FLAG;*)
(*DBG:            break;*)
(*DBG:        default:*)
(*DBG:            break;*)
(*DBG:        }*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void swap_bytes(void *ptr, size_t size) *)
(*DBG:{*)
(*DBG:    uint8_t *bytePtr = (uint8_t *)ptr;*)
(*DBG:    size_t i;*)
(*DBG:    for (i = 0; i < size / 2; ++i) *)
(*DBG:    {*)
(*DBG:        uint8_t temp = bytePtr[i];*)
(*DBG:        bytePtr[i] = bytePtr[size - 1 - i];*)
(*DBG:        bytePtr[size - 1 - i] = temp;*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void trace_reset(void)*)
(*DBG:{*)
(*DBG:    for (size_t i=0; i < VAR_COUNT; i++) *)
(*DBG:    {*)
(*DBG:        force_var(i, false, 0);*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void set_trace(size_t idx, bool forced, void *val)*)
(*DBG:{*)
(*DBG:    if (idx >= 0 && idx < VAR_COUNT) *)
(*DBG:    {*)
(*DBG:        if (endianness == REVERSE_ENDIANNESS)*)
(*DBG:        {*)
(*DBG:            // Aaaaarghhhh... Stupid AVR is Big Endian.*)
(*DBG:            swap_bytes(val, get_var_size(idx));*)
(*DBG:        }*)
(*DBG:*)
(*DBG:        force_var(idx, forced, val);*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)
(*DBG:void set_endianness(uint8_t value)*)
(*DBG:{*)
(*DBG:    if (value == SAME_ENDIANNESS || value == REVERSE_ENDIANNESS)*)
(*DBG:    {*)
(*DBG:        endianness = value;*)
(*DBG:    }*)
(*DBG:}*)
(*DBG:*)