import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '../api/index.js'

export const useTripsStore = defineStore('trips', () => {
  const trips = ref([])
  const currentTrip = ref(null)
  const loading = ref(false)
  const error = ref('')

  async function fetchTrips(params = {}) {
    loading.value = true
    error.value = ''
    try {
      const res = await api.fetchTrips(params)
      trips.value = res.data || []
      return trips.value
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function fetchTrip(id) {
    loading.value = true
    error.value = ''
    try {
      const res = await api.fetchTrip(id)
      currentTrip.value = res.data
      return currentTrip.value
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createTrip(data) {
    const res = await api.createTrip(data)
    return res.data
  }

  async function updateTrip(id, data) {
    await api.updateTrip(id, data)
    if (currentTrip.value && currentTrip.value.id === id) {
      Object.assign(currentTrip.value, data)
    }
  }

  async function deleteTrip(id, deleteFiles = false) {
    await api.deleteTrip(id, deleteFiles)
    trips.value = trips.value.filter(t => t.id !== id)
  }

  return {
    trips, currentTrip, loading, error,
    fetchTrips, fetchTrip, createTrip, updateTrip, deleteTrip,
  }
})
