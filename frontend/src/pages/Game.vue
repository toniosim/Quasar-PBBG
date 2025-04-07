<template>
  <div class="game-interface flex h-full">
    <!-- Left Panel: Actions -->
    <div class="left-panel bg-cyber-dark border-r border-neon-blue w-64 flex-shrink-0 flex flex-col overflow-hidden">
      <div class="p-3 border-b border-neon-blue">
        <h3 class="text-neon-blue font-mono text-lg">{{ $t('actions') }}</h3>
      </div>

      <div class="flex-grow overflow-y-auto p-3 space-y-4">
        <!-- Actions List -->
        <template v-if="gameStore.actions && gameStore.actions.length > 0">
          <div v-for="(action, index) in gameStore.actions" :key="index" class="action-item">
            <q-btn
              :label="action.name"
              :disable="!canPerformAction(action)"
              @click="handleAction(action)"
              class="cyber-button w-full justify-start text-left"
              :class="{'opacity-60': !canPerformAction(action)}"
            >
              <template v-slot:default>
                <div class="flex justify-between items-center w-full">
                  <span>{{ action.name }}</span>
                  <span class="text-xs text-yellow-300">AP: {{ action.ap_cost }}</span>
                </div>
              </template>
            </q-btn>
          </div>
        </template>

        <div v-else class="text-gray-500 font-mono text-center py-4">
          {{ $t('loading') }}
        </div>
      </div>
    </div>

    <!-- Center Panel: Map, Events, Chat -->
    <div class="center-panel flex-grow flex flex-col overflow-hidden">
      <!-- Map and Location -->
      <div class="map-container border-b border-neon-blue p-4">
        <div class="mb-4">
          <h3 class="text-neon-green font-mono text-xl mb-2">
            {{ gameStore.location ? gameStore.location.name : $t('loading') }}
          </h3>
          <p class="text-white">
            {{ gameStore.location ? gameStore.location.description : '' }}
          </p>
        </div>

        <!-- Map Grid -->
        <div class="map-grid grid grid-cols-3 gap-2 mt-4">
          <div
            v-for="(row, rowIndex) in gameStore.map"
            v-if="gameStore.map && gameStore.map.length > 0"
            :key="'row-' + rowIndex"
            class="grid grid-cols-3 gap-2 col-span-3"
          >
            <div
              v-for="(tile, colIndex) in row"
              :key="'tile-' + rowIndex + '-' + colIndex"
              class="map-tile aspect-square flex flex-col items-center justify-center text-center p-1"
              :class="{
                'current': tile && character && tile.x === character.x && tile.y === character.y,
                'clickable': isAdjacentTile(tile)
              }"
              @click="tile && isAdjacentTile(tile) ? moveToTile(tile) : null"
            >
              <template v-if="tile">
                <div class="text-xs" :class="{'text-neon-blue': tile.has_buildings}">
                  {{ tile.name }}
                </div>
                <div v-if="tile.has_buildings" class="mt-1">
                  <i class="material-icons text-xs text-neon-blue">business</i>
                </div>
                <div class="coordinates opacity-50 text-[8px] mt-1">
                  ({{ tile.x }}, {{ tile.y }})
                </div>
              </template>
              <template v-else>
                <div class="text-xs opacity-30">???</div>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs for Events and Chat -->
      <div class="flex-grow flex flex-col overflow-hidden">
        <q-tabs
          v-model="activeTab"
          class="bg-cyber-dark text-white"
          active-color="neon-blue"
          indicator-color="neon-blue"
          align="justify"
          narrow-indicator
        >
          <q-tab name="events" label="Events" icon="event_note" />
          <q-tab name="chat" label="Chat" icon="chat" />
        </q-tabs>

        <q-tab-panels v-model="activeTab" animated class="bg-cyber-dark flex-grow overflow-hidden">
          <!-- Events Tab -->
          <q-tab-panel name="events" class="p-0 h-full overflow-hidden">
            <div class="events-log h-full overflow-y-auto p-3 font-mono">
              <div v-if="gameStore.logs && gameStore.logs.length > 0">
                <div v-for="(log, index) in gameStore.logs" :key="index" class="log-entry mb-2 pb-2 border-b border-cyber-gray">
                  <div class="flex">
                    <span class="text-neon-green text-xs mr-2 whitespace-nowrap">
                      {{ formatTimestamp(log.timestamp) }}
                    </span>
                    <span>{{ log.message }}</span>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-4 text-gray-500">
                No events yet
              </div>
            </div>
          </q-tab-panel>

          <!-- Chat Tab -->
          <q-tab-panel name="chat" class="p-0 h-full overflow-hidden flex flex-col">
            <div class="chat-messages flex-grow overflow-y-auto p-3">
              <div v-if="gameStore.chatMessages && gameStore.chatMessages.length > 0">
                <div v-for="(message, index) in gameStore.chatMessages" :key="index" class="chat-message mb-3">
                  <div class="flex">
                    <span class="text-neon-pink font-mono text-xs mr-2 whitespace-nowrap">
                      {{ formatChatTimestamp(message.timestamp) }}
                    </span>
                    <span class="text-neon-blue font-mono mr-1">[{{ message.character_name }}]:</span>
                    <span>{{ message.message }}</span>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-4 text-gray-500">
                No messages yet
              </div>
            </div>

            <div class="chat-input bg-cyber-dark p-3 border-t border-neon-blue">
              <div class="flex space-x-2">
                <q-input
                  v-model="chatMessage"
                  outlined
                  dense
                  bg-color="cyber-dark"
                  color="neon-blue"
                  :placeholder="$t('chatPlaceholder')"
                  class="flex-grow"
                  @keyup.enter="sendChatMessage"
                />
                <q-btn
                  :label="$t('send')"
                  class="cyber-button"
                  @click="sendChatMessage"
                  :disable="!chatMessage.trim()"
                />
              </div>

              <div class="flex justify-center mt-2">
                <q-btn-toggle
                  v-model="chatChannel"
                  toggle-color="neon-blue"
                  :options="[
                    {label: $t('locationChat'), value: 'location'},
                    {label: $t('globalChat'), value: 'global'},
                    {label: $t('buildingChat'), value: 'building', disable: !isInsideBuilding}
                  ]"
                  class="text-xs"
                />
              </div>
            </div>
          </q-tab-panel>
        </q-tab-panels>
      </div>
    </div>

    <!-- Right Panel: Character Info -->
    <div class="right-panel bg-cyber-dark border-l border-neon-blue w-72 flex-shrink-0 flex flex-col overflow-hidden">
      <q-tabs
        v-model="rightTab"
        class="bg-cyber-dark text-white"
        active-color="neon-pink"
        indicator-color="neon-pink"
        align="justify"
        narrow-indicator
      >
        <q-tab name="character" icon="person" />
        <q-tab name="inventory" icon="inventory_2" />
        <q-tab name="equipment" icon="shield" />
      </q-tabs>

      <q-tab-panels v-model="rightTab" animated class="bg-cyber-dark flex-grow overflow-hidden">
        <!-- Character Tab -->
        <q-tab-panel name="character" class="p-3 h-full overflow-y-auto">
          <div v-if="character">
            <div class="mb-6">
              <h3 class="text-neon-pink font-mono text-xl mb-1">{{ character.name }}</h3>
              <div class="text-xs text-gray-400 mb-4">Level {{ character.level }} - {{ formatExperience(character.experience) }} XP</div>

              <!-- Health, Stamina, AP Bars -->
              <div class="mb-2">
                <div class="flex justify-between items-center mb-1">
                  <span class="text-neon-pink text-xs font-mono">{{ $t('health') }}</span>
                  <span class="text-neon-pink text-xs font-mono">{{ character.health }}/{{ character.max_health }}</span>
                </div>
                <div class="cyber-progress">
                  <div class="cyber-progress-bar cyber-progress-bar-health" :style="{ width: healthPercentage + '%' }"></div>
                </div>
              </div>

              <div class="mb-2">
                <div class="flex justify-between items-center mb-1">
                  <span class="text-neon-green text-xs font-mono">{{ $t('stamina') }}</span>
                  <span class="text-neon-green text-xs font-mono">{{ character.stamina }}/{{ character.max_stamina }}</span>
                </div>
                <div class="cyber-progress">
                  <div class="cyber-progress-bar cyber-progress-bar-stamina" :style="{ width: staminaPercentage + '%' }"></div>
                </div>
              </div>

              <div class="mb-4">
                <div class="flex justify-between items-center mb-1">
                  <span class="text-neon-yellow text-xs font-mono">{{ $t('ap') }}</span>
                  <span class="text-neon-yellow text-xs font-mono">{{ character.ap }}/{{ character.max_ap }}</span>
                </div>
                <div class="cyber-progress">
                  <div class="cyber-progress-bar cyber-progress-bar-ap" :style="{ width: apPercentage + '%' }"></div>
                </div>
              </div>

              <div class="mt-2 text-xs text-neon-blue font-mono">
                <i class="material-icons text-xs align-middle mr-1">payments</i>
                {{ formatMoney(character.money) }} Credits
              </div>
            </div>

            <!-- Stats -->
            <div class="mb-6">
              <h4 class="text-neon-blue font-mono border-b border-cyber-gray pb-1 mb-3">{{ $t('stats') }}</h4>
              <div class="grid grid-cols-2 gap-2">
                <div v-for="(value, stat) in character.stats" :key="stat" class="stat-item">
                  <div class="flex justify-between">
                    <span class="text-gray-400 capitalize">{{ stat }}</span>
                    <span class="text-neon-blue">{{ value }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Skills -->
            <div>
              <h4 class="text-neon-blue font-mono border-b border-cyber-gray pb-1 mb-3">{{ $t('skills') }}</h4>
              <div class="grid grid-cols-2 gap-2">
                <div v-for="(value, skill) in character.skills" :key="skill" class="skill-item">
                  <div class="flex justify-between">
                    <span class="text-gray-400 capitalize">{{ skill }}</span>
                    <span class="text-neon-blue">{{ value }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-4 text-gray-500">
            {{ $t('loading') }}
          </div>
        </q-tab-panel>

        <!-- Inventory Tab -->
        <q-tab-panel name="inventory" class="p-3 h-full overflow-y-auto">
          <h3 class="text-neon-pink font-mono text-xl mb-4">{{ $t('inventory') }}</h3>

          <div v-if="gameStore.inventory && gameStore.inventory.length > 0" class="space-y-3">
            <div v-for="(item, index) in gameStore.inventory" :key="index" class="inventory-item bg-cyber-gray p-2 rounded">
              <div class="flex justify-between items-center">
                <div>
                  <div class="text-neon-blue font-mono">{{ item.definition.name }}</div>
                  <div class="text-xs text-gray-400">{{ item.definition.description }}</div>
                </div>
                <div v-if="item.quantity > 1" class="text-neon-pink font-mono text-sm">
                  x{{ item.quantity }}
                </div>
              </div>

              <div class="flex justify-end mt-2 space-x-2">
                <q-btn
                  v-if="item.definition.type === 'equipment'"
                  flat
                  dense
                  size="sm"
                  color="neon-blue"
                  icon="layers"
                  label="Equip"
                  @click="equipItem(item.id)"
                />
                <q-btn
                  v-if="item.definition.type === 'consumable'"
                  flat
                  dense
                  size="sm"
                  color="neon-green"
                  icon="local_dining"
                  label="Use"
                  @click="useItem(item.id)"
                />
              </div>
            </div>
          </div>

          <div v-else class="text-center py-4 text-gray-500">
            Your inventory is empty
          </div>
        </q-tab-panel>

        <!-- Equipment Tab -->
        <q-tab-panel name="equipment" class="p-3 h-full overflow-y-auto">
          <h3 class="text-neon-pink font-mono text-xl mb-4">{{ $t('equipment') }}</h3>

          <div v-if="Object.keys(gameStore.equipment).length > 0" class="space-y-4">
            <div v-for="(item, slot) in gameStore.equipment" :key="slot" class="equipment-item">
              <div class="bg-cyber-gray p-2 rounded">
                <div class="flex justify-between items-center">
                  <div>
                    <div class="text-neon-blue font-mono">{{ item.definition.name }}</div>
                    <div class="text-xs text-gray-400">{{ item.definition.description }}</div>
                    <div class="text-xs text-neon-pink mt-1">{{ formatSlotName(slot) }}</div>
                  </div>
                </div>

                <div class="flex justify-end mt-2">
                  <q-btn
                    flat
                    dense
                    size="sm"
                    color="red"
                    icon="layers_clear"
                    label="Unequip"
                    @click="unequipItem(slot)"
                  />
                </div>
              </div>
            </div>
          </div>

          <div v-else class="text-center py-4 text-gray-500">
            No equipment
          </div>
        </q-tab-panel>
      </q-tab-panels>
    </div>

    <!-- Action modals -->
    <q-dialog v-model="moveModal" persistent>
      <q-card class="bg-cyber-dark border border-neon-blue">
        <q-card-section>
          <div class="text-neon-blue font-mono text-xl">{{ $t('move') }}</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="text-white">
            {{ $t('chooseDirection') }}:
          </div>

          <div class="directions-grid grid grid-cols-3 gap-2 max-w-xs mx-auto mt-4">
            <q-btn
              v-for="option in currentDirectionOptions"
              :key="option.direction"
              :label="$t(option.direction)"
              @click="confirmMove(option)"
              class="cyber-button"
            />
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat :label="$t('cancel')" color="red" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="buildingModal" persistent>
      <q-card class="bg-cyber-dark border border-neon-blue">
        <q-card-section>
          <div class="text-neon-blue font-mono text-xl">{{ $t('enterBuilding') }}</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="text-white mb-4">
            {{ $t('chooseBuilding') }}:
          </div>

          <q-list bordered class="rounded-borders">
            <q-item
              v-for="building in currentBuildingOptions"
              :key="building.building_id"
              clickable
              v-ripple
              @click="confirmEnterBuilding(building)"
            >
              <q-item-section>
                <q-item-label class="text-neon-blue">{{ building.label }}</q-item-label>
                <q-item-label caption>{{ building.description }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat :label="$t('cancel')" color="red" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="generalActionModal" persistent>
      <q-card class="bg-cyber-dark border border-neon-blue">
        <q-card-section>
          <div class="text-neon-blue font-mono text-xl">{{ currentAction?.name }}</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="text-white mb-4">
            {{ currentAction?.description }}
          </div>

          <div v-if="currentActionOptions && currentActionOptions.length > 0">
            <q-select
              v-model="selectedActionOption"
              :options="currentActionOptions"
              label="Select Option"
              color="neon-blue"
              outlined
              dark
              bg-color="cyber-dark"
            />
          </div>

          <div v-else class="text-neon-yellow">
            AP Cost: {{ currentAction?.ap_cost }}
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat :label="$t('cancel')" color="red" v-close-popup />
          <q-btn :label="$t('confirm')" color="neon-blue" @click="confirmGeneralAction" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useGameStore } from 'src/stores/game-store';
import { useQuasar } from 'quasar';

export default defineComponent({
  name: 'GamePage',

  setup() {
    const { t } = useI18n();
    const gameStore = useGameStore();
    const $q = useQuasar();

    // Tabs
    const activeTab = ref('events');
    const rightTab = ref('character');

    // Chat
    const chatMessage = ref('');
    const chatChannel = ref('location');

    // Modals
    const moveModal = ref(false);
    const buildingModal = ref(false);
    const generalActionModal = ref(false);

    // Action data
    const currentAction = ref<any>(null);
    const currentDirectionOptions = ref<any[]>([]);
    const currentBuildingOptions = ref<any[]>([]);
    const currentActionOptions = ref<any[]>([]);
    const selectedActionOption = ref<any>(null);

    // Character data
    const character = computed(() => gameStore.character);

    // Health, stamina, AP percentages
    const healthPercentage = computed(() => gameStore.healthPercentage);
    const staminaPercentage = computed(() => gameStore.staminaPercentage);
    const apPercentage = computed(() => gameStore.apPercentage);

    // Is character inside a building
    const isInsideBuilding = computed(() => gameStore.isInsideBuilding);

    // Format timestamp for logs
    const formatTimestamp = (timestamp: string) => {
      if (!timestamp) return '';
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    // Format timestamp for chat
    const formatChatTimestamp = (timestamp: string) => {
      if (!timestamp) return '';
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    // Format money
    const formatMoney = (amount: number) => {
      return amount.toLocaleString();
    };

    // Format experience
    const formatExperience = (xp: number) => {
      return xp.toLocaleString();
    };

    // Format slot name
    const formatSlotName = (slot: string) => {
      // Convert camelCase or snake_case to readable format
      return slot
        .replace(/([A-Z])/g, ' $1') // Insert space before capital letters
        .replace(/_/g, ' ') // Replace underscores with spaces
        .trim()
        .toLowerCase()
        .replace(/\b\w/g, (l) => l.toUpperCase()); // Capitalize first letter of each word
    };

    // Check if an action can be performed (has enough AP)
    const canPerformAction = (action: any) => {
      if (!character.value) return false;
      return character.value.ap >= action.ap_cost;
    };

    // Check if a tile is adjacent to the character's position
    const isAdjacentTile = (tile: any) => {
      if (!tile || !character.value) return false;

      const dx = Math.abs(tile.x - character.value.x);
      const dy = Math.abs(tile.y - character.value.y);

      // Consider both orthogonal and diagonal movement
      return (dx <= 1 && dy <= 1) && !(dx === 0 && dy === 0);
    };

    // Move to a tile when clicked on the map
    const moveToTile = (tile: any) => {
      if (!tile || !isAdjacentTile(tile)) return;

      // Find the direction to move
      const dx = tile.x - character.value!.x;
      const dy = tile.y - character.value!.y;

      let direction = '';
      if (dx === 0 && dy === -1) direction = 'north';
      else if (dx === 1 && dy === -1) direction = 'northeast';
      else if (dx === 1 && dy === 0) direction = 'east';
      else if (dx === 1 && dy === 1) direction = 'southeast';
      else if (dx === 0 && dy === 1) direction = 'south';
      else if (dx === -1 && dy === 1) direction = 'southwest';
      else if (dx === -1 && dy === 0) direction = 'west';
      else if (dx === -1 && dy === -1) direction = 'northwest';

      // Perform move action
      if (direction) {
        gameStore.performAction('MOVE', { direction });
      }
    };

    // Handle action button click
    const handleAction = (action: any) => {
      // Store current action
      currentAction.value = action;

      // Show appropriate modal based on action type
      if (action.type === 'MOVE') {
        // Show move modal with direction options
        currentDirectionOptions.value = action.data?.options || [];
        moveModal.value = true;
      } else if (action.type === 'ENTER_BUILDING') {
        // Show building modal with building options
        currentBuildingOptions.value = action.data?.options || [];
        buildingModal.value = true;
      } else if (action.type === 'EXIT_BUILDING') {
        // Exit building doesn't need options
        gameStore.performAction('EXIT_BUILDING');
      } else {
        // Show general action modal
        currentActionOptions.value = action.data?.options || [];
        if (currentActionOptions.value.length > 0) {
          selectedActionOption.value = currentActionOptions.value[0];
        }
        generalActionModal.value = true;
      }
    };

    // Confirm move action
    const confirmMove = (option: any) => {
      moveModal.value = false;
      gameStore.performAction('MOVE', { direction: option.direction });
    };

    // Confirm enter building action
    const confirmEnterBuilding = (building: any) => {
      buildingModal.value = false;
      gameStore.performAction('ENTER_BUILDING', { building_id: building.building_id });
    };

    // Confirm general action
    const confirmGeneralAction = () => {
      generalActionModal.value = false;

      // Prepare action data based on whether there are options
      let actionData = {};
      if (currentActionOptions.value.length > 0 && selectedActionOption.value) {
        actionData = { option: selectedActionOption.value.value };
      }

      // Perform the action
      gameStore.performAction(currentAction.value.type, actionData);
    };

    // Send chat message
    const sendChatMessage = () => {
      if (!chatMessage.value.trim()) return;

      gameStore.sendChatMessage(chatMessage.value, chatChannel.value);
      chatMessage.value = '';
    };

    // Equipment actions
    const equipItem = (itemId: string) => {
      $q.dialog({
        title: 'Equip Item',
        message: 'Are you sure you want to equip this item?',
        cancel: true,
        persistent: true
      }).onOk(() => {
        // Call backend API to equip item
        console.log('Equip item:', itemId);
      });
    };

    const unequipItem = (slot: string) => {
      $q.dialog({
        title: 'Unequip Item',
        message: 'Are you sure you want to unequip this item?',
        cancel: true,
        persistent: true
      }).onOk(() => {
        // Call backend API to unequip item
        console.log('Unequip item from slot:', slot);
      });
    };

    const useItem = (itemId: string) => {
      $q.dialog({
        title: 'Use Item',
        message: 'Are you sure you want to use this item?',
        cancel: true,
        persistent: true
      }).onOk(() => {
        // Call backend API to use item
        console.log('Use item:', itemId);
      });
    };

    // Watch for changes in right panel tab
    watch(rightTab, (newTab) => {
      // Load data based on active tab
      if (newTab === 'inventory') {
        gameStore.loadInventory();
      } else if (newTab === 'equipment') {
        gameStore.loadEquipment();
      }
    });

    return {
      // Store
      gameStore,

      // Tabs
      activeTab,
      rightTab,

      // Character data
      character,
      healthPercentage,
      staminaPercentage,
      apPercentage,
      isInsideBuilding,

      // Chat
      chatMessage,
      chatChannel,
      sendChatMessage,

      // Modals
      moveModal,
      buildingModal,
      generalActionModal,

      // Action data
      currentAction,
      currentDirectionOptions,
      currentBuildingOptions,
      currentActionOptions,
      selectedActionOption,

      // Methods
      formatTimestamp,
      formatChatTimestamp,
      formatMoney,
      formatExperience,
      formatSlotName,
      canPerformAction,
      isAdjacentTile,
      moveToTile,
      handleAction,
      confirmMove,
      confirmEnterBuilding,
      confirmGeneralAction,
      equipItem,
      unequipItem,
      useItem,

      // i18n
      $t: t
    };
  }
});
</script>

<style scoped>
.game-interface {
  height: calc(100vh - 48px); /* Subtract header height */
}

/* Map tile styling */
.map-tile {
  min-height: 60px;
  font-size: 0.7rem;
  transition: all 0.2s ease;
}

.map-tile.current {
  border-color: #ff00ff;
  box-shadow: 0 0 10px rgba(255, 0, 255, 0.8), inset 0 0 10px rgba(255, 0, 255, 0.3);
}

.map-tile.clickable {
  border-color: rgba(0, 240, 255, 0.4);
  cursor: pointer;
}

.map-tile.clickable:hover {
  border-color: #00f0ff;
  box-shadow: 0 0 8px rgba(0, 240, 255, 0.6), inset 0 0 5px rgba(0, 240, 255, 0.2);
  transform: translateY(-2px);
}

/* Action item styling */
.action-item {
  transition: transform 0.2s ease;
}

.action-item:hover {
  transform: translateY(-2px);
}

/* Direction grid for movement */
.directions-grid {
  grid-template-areas:
    "nw n ne"
    "w . e"
    "sw s se";
}

.directions-grid button:nth-child(1) { grid-area: nw; }
.directions-grid button:nth-child(2) { grid-area: n; }
.directions-grid button:nth-child(3) { grid-area: ne; }
.directions-grid button:nth-child(4) { grid-area: w; }
.directions-grid button:nth-child(5) { grid-area: e; }
.directions-grid button:nth-child(6) { grid-area: sw; }
.directions-grid button:nth-child(7) { grid-area: s; }
.directions-grid button:nth-child(8) { grid-area: se; }

/* Custom scrollbars for panels */
.left-panel::-webkit-scrollbar,
.events-log::-webkit-scrollbar,
.chat-messages::-webkit-scrollbar {
  width: 4px;
}

.left-panel::-webkit-scrollbar-track,
.events-log::-webkit-scrollbar-track,
.chat-messages::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.2);
}

.left-panel::-webkit-scrollbar-thumb,
.events-log::-webkit-scrollbar-thumb,
.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(0, 240, 255, 0.5);
  border-radius: 2px;
}

.left-panel::-webkit-scrollbar-thumb:hover,
.events-log::-webkit-scrollbar-thumb:hover,
.chat-messages::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 240, 255, 0.8);
}
</style>